# utility imports
from pathlib import Path
import os
from django.shortcuts import render
from django.http import HttpResponse
from app.tex_gen import createTextFile
from app.data_gen import data_generator
from openresume.settings import BASE_DIR,MEDIA_ROOT,MEDIA_URL,STATIC_DIR
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# model imports
from app.models import *
from django.contrib.auth.models import User

#path declarations

DATA_ROOT = os.path.join(MEDIA_ROOT,'data')
LATEX_ROOT = os.path.join(STATIC_DIR,'latex')
PDFS_ROOT = os.path.join(STATIC_DIR,'pdfs')
# Create your views here.

#classes

class projectObj:
    def __init__(self, title_string, date_string,club_string, github_string, des_string, title, date, club, github, des,ind):
        self.title_string = title_string
        self.date_string = date_string
        self.club_string = club_string
        self.github_string = github_string
        self.des_string = des_string
        self.title = title
        self.date = date
        self.club = club
        self.github = github
        self.des = des
        self.ind = ind

class porObj:
    def __init__(self,por_string,por_des_string,ind,Por,PorDesc):
        self.por_string = por_string
        self.por_des_string = por_des_string
        self.ind = ind
        self.Por = Por
        self.PorDesc = PorDesc


class achObj:
    def __init__(self,ach_string,ach_des_string,ind,Ach,AchDes):
        self.ach_string = ach_string
        self.ach_des_string = ach_des_string
        self.ind = ind
        self.Ach = Ach
        self.AchDes = AchDes

class expObj:
    def __init__(self,exp_string,exp_des_string,ind,Exp,ExpDes):
        self.exp_string = exp_string
        self.exp_des_string = exp_des_string
        self.ind = ind
        self.Exp = Exp
        self.ExpDes = ExpDes

class courseObj:
    def __init__(self, course_string,Course):
        self.course_string = course_string
        self.Course = Course




@login_required()
def index(request,pk):
   
    # initialize the dictionary to be sent to the template.
    my_dict = {}

    
    # collected the details of the user.
    us = User.objects.get(username = request.user)
    resume_mod = Resume.objects.get(id=pk)
    resume_file_name = str(resume_mod.rFile)

    res_rel = us.user_resume_relation_set.first()
    resume_list = list(Resume.objects.filter(user_resume_relation = res_rel))

    if resume_mod not in resume_list:
        return render(request,'pdfgen/wrongIndex.html')

    #reading the lines of the data file to be injected into index template.
    data_file_lines = open(os.path.join(DATA_ROOT,resume_file_name),'r').readlines()


    #count of each section fields to be looped in the template.
    projectsCount = 0
    coursesCount = 0
    porCount = 0
    achCount = 0
    expCount = 0

    
    #filling my_dict with corresponding data and also keeping track of count of fields
    for line in data_file_lines:
        if line != "":
            tmp = line.split('#')
            if len(tmp) != 2:
                continue
            tmp_key = str(tmp[0])
            my_dict[tmp_key] = str(tmp[1])
            
            if "course" in tmp_key:
                coursesCount +=1
            elif "proTitle" in tmp_key and len(tmp_key) == 9:
                projectsCount +=1
            elif "por" in tmp_key and len(tmp_key) == 4:
                porCount +=1
            elif "ach" in tmp_key and len(tmp_key) == 4:
                achCount += 1
            elif "exp" in tmp_key and len(tmp_key) == 4:
                expCount +=1
    
    
    #counts of section fields sent successfully
    my_dict["projectsCount"] = projectsCount
    my_dict["porCount"] = porCount
    my_dict["coursesCount"] = coursesCount
    my_dict["achCount"] = achCount
    my_dict["expCount"] = expCount

    #print("achCount = ", achCount)
    
    #initializing the lists of section fields to be sent
    project_list = []
    exp_list = []
    courses_list = []
    ach_list = []
    por_list = []

    #filling projects list with format -> projectObj(title_string, date_string, club_string, github_string, des_string, corresponding values)
    for i in range(projectsCount):
        title_string = "proTitle" + str(i+1)
        date_string = "proDate" + str(i+1)
        club_string = "clubName" + str(i+1)
        github_string = "githubLink" + str(i+1)
        des_string = "proDes" + str(i+1)

        project_list.append(projectObj(title_string , date_string, club_string, github_string, des_string, my_dict[title_string], my_dict[date_string], my_dict[club_string], my_dict[github_string], my_dict[des_string],i+1))
    my_dict["project_list"] = project_list
    

    # filling por_list with values of format -> porObj()
    for i in range(porCount):
        por_string = "por" + str(i+1)
        por_des_string = "porDesc" + str(i+1)
        por_list.append(porObj(por_string,por_des_string, i+1, my_dict[por_string], my_dict[por_des_string]))
    my_dict["por_list"] = por_list

    
    # filling por_list with values of format -> achObj()
    for i in range(achCount):
        ach_string = "ach" + str(i+1)
        ach_des_string = "achDes" + str(i+1)
        ach_list.append(achObj(ach_string,ach_des_string,i+1,my_dict[ach_string],my_dict[ach_des_string]))
    my_dict["ach_list"] = ach_list

    
    # filling por_list with values of format -> courseObj()
    for i in range(coursesCount):
        course_string = "course" + str(i+1)
        courses_list.append(courseObj(course_string,my_dict[course_string]))
    my_dict["courses_list"] = courses_list

    
    # filling por_list with values of format -> expObj()
    for i in range(expCount):
        exp_string = "exp" + str(i+1)
        exp_des_string = "expDes" + str(i+1)
        exp_list.append(expObj(exp_string ,exp_des_string , i+1,my_dict[exp_string],my_dict[exp_des_string]))
    my_dict["exp_list"] = exp_list


    # the name of the pdf to be passed for displaying in the top-> initialization and added to my_dict
    pdf_string = 'pdfs/' + str(resume_mod.pdfFile)

    if os.path.getsize('static/'+pdf_string)==0:
        pdf_string = 'data/display_resume.pdf'
        
    my_dict['pdf_string'] = pdf_string

    

    """****************************************************************************************************************************"""


    if request.method == 'POST':

        #input dictionary
        md = request.POST
        
        
        print(md) 
        
        # initializing section lists
        education=[]
        internships=[]
        projects=[]
        course=[]
        por=[]
        achievements=[]
        
        # edu_list = ['MTech', 'BTech','Seniory Secondary','Secondary']
        education = [
                     ["M.Tech",md["mtechBoard"], md["mtechGrade"],md["mtechYear"]],
                     ["B.Tech",md["btechBoard"],md["btechGrade"],md["btechYear"]],
                     ["Secondary senior",md["ssBoard"],md["ssGrade"],md["ssYear"]],
                     ["Secondary",md["sBoard"],md["sGrade"],md["sYear"]],
                    ]
        #education update
        new_edu=resume_mod.education
        new_edu.mtechBoard = md['mtechBoard']
        new_edu.mtechGrade = md['mtechGrade']
        new_edu.mtechYear = md['mtechYear']
        new_edu.btechBoard = md['btechBoard']
        new_edu.btechGrade = md['btechGrade']
        new_edu.btechYear = md['btechYear']
        new_edu.ssBoard = md['ssBoard']
        new_edu.ssGrade = md['ssGrade']
        new_edu.ssYear = md['ssYear']
        new_edu.sBoard = md['sBoard']
        new_edu.sGrade = md['sGrade']
        new_edu.sYear = md['sYear']
        new_edu.save()
        
        if(md["mtechBoard"]=="" and md["mtechYear"]=="" and md["mtechGrade"]==""):
            education.pop(0)

        
        #collecting internships data     
        if ('exp' in request.POST.keys()):
            exp_titles = request.POST.getlist('exp')
            exp_descs = request.POST.getlist('expDes')
            prev_exp=resume_mod.experience_set.all()
            prev_exp_count=len(prev_exp)
            new_exp_count=len(exp_titles)
            for j in range(min(prev_exp_count,new_exp_count)):
                prev_exp[j].exp=exp_titles[j]
                prev_exp[j].expDes=exp_descs[j]
                prev_exp[j].save()
            if prev_exp_count>new_exp_count:
                for j in range(new_exp_count,prev_exp_count):
                    prev_exp[j].delete()
            else:
                for j in range(prev_exp_count,new_exp_count):
                    new_exp=Experience(resume=resume_mod,exp=exp_titles[j],expDes=exp_descs[j])
                    new_exp.save()
            
            
            for i in range(len(exp_titles)):
                internships.append([exp_titles[i], exp_descs[i]])
                print(exp_descs[i])
               

        #collecting projects data
        #format ["title1","club1","desc1","link1","date1"]

        if('proTitle' in request.POST.keys()):
            pro_titles = request.POST.getlist('proTitle')
            pro_clubs = request.POST.getlist('clubName')
            pro_descs = request.POST.getlist('proDes')
            pro_links = request.POST.getlist('githubLink')
            pro_dates = request.POST.getlist('proDate')
            prev_pro=resume_mod.projects_set.all()
            prev_pro_count=len(prev_pro)
            new_pro_count=len(pro_titles)
            for j in range(min(prev_pro_count,new_pro_count)):
                prev_pro[j].proTitle=pro_titles[j]
                prev_pro[j].proDes=pro_descs[j]
                prev_pro[j].clubName=pro_clubs[j]
                prev_pro[j].githubLink=pro_links[j]
                prev_pro[j].proDate=pro_dates[j]
                prev_pro[j].save()
            if prev_pro_count>new_pro_count:
                for j in range(new_pro_count,prev_pro_count):
                    prev_pro[j].delete()
            else:
                for j in range(prev_pro_count,new_pro_count):
                    new_pro=Projects(resume=resume_mod,proTitle=pro_titles[j],proDes=pro_descs[j],clubName=pro_clubs[j],githubLink=pro_links[j],proDate=pro_dates[j])
                    new_pro.save()
            for i in range(len(pro_titles)):
                projects.append([pro_titles[i],pro_clubs[i], pro_descs[i], pro_links[i], pro_dates[i]])
                
            
        
        
        #collecting course data

        if('course' in request.POST.keys()):
            course = request.POST.getlist('course')
            prev_cou=resume_mod.course_set.all()
            prev_cou_count=len(prev_cou)
            new_cou_count=len(course)

            for j in range(min(prev_cou_count,new_cou_count)):
                prev_cou[j].name=course[j]
                prev_cou[j].save()
            if prev_cou_count>new_cou_count:
                for j in range(new_cou_count,prev_cou_count):
                    prev_cou[j].delete()
            else:
                for j in range(prev_cou_count,new_cou_count):
                    new_cou=Course(resume=resume_mod,name=course[j])
                    new_cou.save()

        
        #collecting por data

        if ('por' in request.POST.keys()):
            por_titles = request.POST.getlist('por')
            por_descs = request.POST.getlist('porDesc')
            prev_por=resume_mod.por_set.all()
            prev_por_count=len(prev_por)
            new_por_count=len(por_titles)
            for j in range(min(prev_por_count,new_por_count)):
                prev_por[j].por=por_titles[j]
                prev_por[j].porDesc=por_descs[j]
                prev_por[j].save()
            if prev_por_count>new_por_count:
                for j in range(new_por_count,prev_por_count):
                    prev_por[j].delete()
            else:
                for j in range(prev_por_count,new_por_count):
                    new_por=Por(resume=resume_mod,por=por_titles[j],porDesc=por_descs[j])
                    new_por.save()

            for i in range(min(len(por_titles), len(por_descs))):
                por.append([por_titles[i], por_descs[i]])
                


        
        #collecting ach data

        if('ach' in request.POST.keys()):
            ach_titles = request.POST.getlist('ach')
            ach_descs = request.POST.getlist('achDes')
            prev_ach=resume_mod.achievement_set.all()
            prev_ach_count=len(prev_ach)
            new_ach_count=len(ach_titles)
            for j in range(min(prev_ach_count,new_ach_count)):
                prev_ach[j].ach=ach_titles[j]
                prev_ach[j].achDes=ach_descs[j]
                prev_ach[j].save()
            if prev_ach_count>new_ach_count:
                for j in range(new_ach_count,prev_ach_count):
                    prev_ach[j].delete()
            else:
                for j in range(prev_ach_count,new_ach_count):
                    new_ach=Achievement(resume=resume_mod,ach=ach_titles[j],achDes=ach_descs[j])
                    new_ach.save()        


             
                
            for i in range(min(len(ach_titles),len(ach_descs))):
                achievements.append([ach_titles[i], ach_descs[i]])
                
        

        #collecting technical skills
        techskills = {
            "Programming Languages": md['pLanguages'],
            "Web Technogies": md['webTechs'],
            "DBMS": md['dbms'],
            "OS": md['os'],
            "Miscellaneous": md['miscellaneous'],
            "Other skills": md['otherSkills'],
        }
        #tech skills update
        pro_tech=resume_mod.techskills
        pro_tech.pLanguages = md['pLanguages']
        pro_tech.webTechs = md['webTechs']
        pro_tech.dbms = md['dbms']
        pro_tech.os = md['os']
        pro_tech.miscellaneous = md['miscellaneous']
        pro_tech.others = md['otherSkills']
        pro_tech.save()


        #profile model update
        pro_model=resume_mod.profile
        print(pro_model)
        pro_model.name=md['name'] 
        pro_model.roll=md['roll']
        pro_model.stream=md['stream']
        pro_model.programme=md['programme']
        pro_model.minor=md['minor']
        pro_model.email=md['email']
        pro_model.webmail=md['webmail']
        pro_model.mobile=str(md['mobile'])
        pro_model.linkedIn=md['linkedIn']
        pro_model.save()           
        print(pro_model) 
        if md['save_flag']=="true":
            data_generator(md,resume_file_name, achievements =  achievements,por = por, course = course, projects = projects, internships = internships)
            return redirect('/index/'+str(pk)+'/')
        

        
        
        

        #generating the LaTex file 
        createTextFile(latex_file_name = str(resume_mod.latexFile), name = md['name'], rollno=str(md['roll']), stream = md['stream'],branch=md['programme'],minor=md['minor'],college="IIT Guwahati",
            email= md['email'],iitgmail=md['webmail'],mobileno= str(md['mobile']),
            linkedin= md['linkedIn'],
            education=education,
            internships=internships,
            projects=projects,
            techskills=techskills,
            keyCourses=course,
            por=por,
            achievements=achievements)

        # updating corresponding data file
        data_generator(md,resume_file_name, achievements =  achievements,por = por, course = course, projects = projects, internships = internships)
        
        # compiling the latex file and generating pdf file
        pdflatex_cmd_str = 'pdflatex '+ '-output-directory=' + str(PDFS_ROOT)+ ' ' + str(LATEX_ROOT) +'\\'+ str(resume_mod.latexFile)
        os.system(pdflatex_cmd_str)

        #deleting auxilary files for efficient memory usage.
        plain_name = str(resume_mod.latexFile)
        plain_name = 'static/pdfs/'+plain_name[:-4]
        os.remove(plain_name + '.aux')
        os.remove(plain_name + '.out')
        os.remove(plain_name + '.log')
        
        return redirect('/index/'+str(pk)+'/')
       
    return render(request,'app/index.html',context = my_dict)




@login_required()
def results(request,pk):
    #checking whether the requested resume is permitted for the current user
    us = User.objects.get(username = request.user)
    resume_mod = Resume.objects.get(id=pk)
    res_rel = us.user_resume_relation_set.first()
    resume_list = list(Resume.objects.filter(user_resume_relation = res_rel))

    
    if resume_mod not in resume_list:
        return render(request,'pdfgen/wrongIndex.html')

    
    #pdf_location = '{% static \'pdfs/'+str(resume_mod.pdfFile)+ '\' %}'
    pdf_loc = '/pdfs/' + str(resume_mod.pdfFile)
    latex_loc = '/latex/'+str(resume_mod.latexFile)
    results_dict = {
                    "pdf_loc": pdf_loc,
                    'latex_loc':latex_loc,
                    }
    return render(request,'pdfgen/results.html',context = results_dict)

@login_required()
def home(request):

    us = User.objects.get(username = request.user)
    res_rel = us.user_resume_relation_set.first()
    if res_rel is None:
        res_rel = User_resume_relation()
        res_rel.user = us
        res_rel.save()
    resumes_list = list(Resume.objects.filter(user_resume_relation = res_rel))
    print(resumes_list)

    home_dict = {"name":us.first_name}
    home_dict["Resumes"] = resumes_list



    
    # if len(resumes_list)==0:
    #     return redirect('index/')

    if request.method == 'POST':
        requestDir = request.POST

        print(requestDir)
        
        if requestDir["delete_flag"]=='true':
            delete_resume_id = int(requestDir['delete_resume_id'])
            del_res = Resume.objects.get(id = delete_resume_id)

            delete_data_file = str(del_res.rFile)
            delete_pdf_file = str(del_res.pdfFile)
            delete_latex_file = str(del_res.latexFile)

            delete_data_file = 'media/data/'+delete_data_file
            delete_pdf_file = 'static/pdfs/'+delete_pdf_file
            delete_latex_file = 'static/latex/'+delete_latex_file

            os.remove(delete_data_file)
            os.remove(delete_pdf_file)
            os.remove(delete_latex_file)
            del_res.delete()
            return redirect('/')


        if requestDir["newResume"]=="":
            print("form submitted successfully..")
            return redirect('/')
        else:
            #creating a new instance and setting the parameters when ever a user request for new resume generation..
            resume_mod = Resume()
            resume_mod.name = requestDir["newResume"]
            resume_mod.save()
            resume_id = resume_mod.id

            #setting the object attributes
            
            new_data_file_name = 'datafile_'+str(resume_id)+'.txt'
            new_pdf_file_name = 'latexFile_'+str(resume_id)+'.pdf'
            new_latex_file_name = 'latexFile_'+str(resume_id)+'.tex'
            open(os.path.join(DATA_ROOT,new_data_file_name),'w').close()
            open(os.path.join(PDFS_ROOT,new_pdf_file_name),'w').close()
            open(os.path.join(LATEX_ROOT,new_latex_file_name),'w').close()
            


            resume_mod = Resume.objects.get(id = resume_id)
            resume_mod.rFile.name = new_data_file_name
            resume_mod.pdfFile = new_pdf_file_name
            resume_mod.latexFile = new_latex_file_name

            resume_mod.save()
            pro_mod=Profile(resume=resume_mod)
            pro_mod.save()
            tech_mod=Techskills(resume=resume_mod)
            tech_mod.save()
            edu_mod=Education(resume=resume_mod)
            edu_mod.save()
            res_rel.resumes.add(resume_mod)

            redirect_url = '/index/'+str(resume_mod.id)+'/'
            print(redirect_url)
            return redirect(redirect_url)

    return render(request,'app/home.html',context = home_dict)

"""
def send(request):
    toh=request.POST['to']
    print(toh)
    mail_content = '''
    '''
    sender_address = 'resumegenerator112@gmail.com'
    sender_pass = 'Resumegenerator123'
    receiver_address = toh
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Hi bro Nuv thoppp!!!!!!!'
    message.attach(MIMEText(mail_content, 'plain'))
    attach_file_name ='static/pdfs/'+ Resume.objects.get(id=request.POST['pk']).pdfFile
    print
    attach_file = open(attach_file_name, 'rb') 
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload((attach_file).read())
    encoders.encode_base64(payload) 
    payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    message.attach(payload)
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls() 
    session.login(sender_address, sender_pass) 
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')
    return redirect('home')
"""
