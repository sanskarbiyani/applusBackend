from operator import le
from rest_framework import status, renderers
from django.http import FileResponse, HttpResponse
from rest_framework.response import Response
from rest_framework import generics, viewsets
from importlib import import_module,reload
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from dynamic_models.models import  ModelSchema, FieldSchema, Lists
from users.serializers import CreateList_group_linkSerializer, List_group_linkSerializer, ResetFormEmailRequestSerializer, SetNewFormSerializer
from ddmapp.serializers import  GroupListSerializer, ListSerializer, GeneralSerializer,FieldSchemasSerializer,List_Database_Serializer, ModelSchemasSerializer, UpdateFieldSchemasSerializer, UserSerializer, LogentriesSerializer
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from .models import ParserSerializer, UploadPdf, FinalSerializer
from .models import Parser, FinalCV
from users.models import NewUser, User_group_link
from .models import ResumeSerializer
from ddmapp.admin import unregister, register, reregister
from ddmapp.models import List_Database, List_group_link, LogEntries 
from django.shortcuts import redirect, render
from django.urls import clear_url_caches 
from django.contrib.auth.models import Group, Permission, User
from django.http import HttpResponse
import nltk
from wsgiref.util import FileWrapper
from django.conf import settings
from rest_framework import permissions
import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import docx2txt
import re
import operator
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
set(stopwords.words('english'))
from sumy.summarizers.text_rank import TextRankSummarizer
from wordcloud import WordCloud
from nltk.probability import FreqDist
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pdfminer.high_level import extract_text
import os
import numpy as np
import mimetypes
from cachetools import TTLCache
import shutil
import heapq
from django.core.files.storage import FileSystemStorage
from dynamic_models.factory import ModelFactory, FieldFactory


from operator import le
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics, viewsets
from importlib import import_module,reload
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from dynamic_models.models import  ModelSchema, Lists
from users.serializers import CreateList_group_linkSerializer
from ddmapp.serializers import  List_Database_Serializer, ModelSchemasSerializer
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from .models import ParserSerializer, UploadPdf, FinalSerializer
from .models import Parser, FinalCV
from users.models import NewUser, User_group_link
from .models import ResumeSerializer
from ddmapp.admin import unregister, register, reregister
from ddmapp.models import List_Database, List_group_link, LogEntries 
from django.shortcuts import redirect, render
from django.urls import clear_url_caches 
from django.contrib.auth.models import Group, Permission, User
from django.http import HttpResponse
import nltk
from django.conf import settings
from rest_framework import permissions
import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import docx2txt
import re
import operator
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
set(stopwords.words('english'))
from wordcloud import WordCloud
from nltk.probability import FreqDist
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pdfminer.high_level import extract_text
import os
import numpy as np
from cachetools import TTLCache
import shutil
import heapq
import spacy
from django.core.files.storage import FileSystemStorage
from dynamic_models.factory import ModelFactory, FieldFactory
from spacy.matcher import Matcher
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# NAME_PATTERN = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
# nlp = spacy.load('en_core_web_sm')


def extract_name1(res_doc):   
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)
    pattern = [[{'POS': 'PROPN'}, {'POS': 'PROPN'}]]
    matcher.add('NAME', pattern)
    doc = nlp(res_doc)
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text



def extract_emails(resume_text):
    try:
        EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
        EMAIL_REG2 = re.compile(r'[A-Z0-9\.\-+_]+@[A-Z0-9\.\-+_]+\.[A-Z]+')
        
        email = re.findall(EMAIL_REG, resume_text)
        email2 = re.findall(EMAIL_REG2, resume_text)
        if email:
            return list(set(email))
        elif email2:
            return list(set(email2))
        else:
            print("Please refer Resume for Email")
    except:
        print("Extract Email Issue")

def read_word_resume(word_doc):
    try:
        resume = docx2txt.process(word_doc)
        resume = str(resume)
        text =  ''.join(resume)
        text = text.replace("\n", "")
        if text:
            return text
    except:
        print("Read_Word_Issue")

other_stop_words = ['junior', 'senior','experience','etc','job','work','company','technique','candidate','skill','skills','language','menu','inc','new','plus','years','technology','organization','ceo',
                    'cto','account','manager','data','scientist','mobile','developer','product','revenue','strong','impact','ability','lower','cae','vehicle','good','problems','global','seat','speed']

def clean_job_decsription(jd):                      ## Clean the Text
        clean_jd = jd.lower()                       # Lower
        clean_jd = re.sub(r'[^\w\s]', '', clean_jd) # remove punctuation
        clean_jd = clean_jd.strip()                 # remove trailing spaces
        clean_jd = re.sub('[0-9]+', '', clean_jd)   # remove numbers
        clean_jd = word_tokenize(clean_jd)          # tokenize 
        stop = stopwords.words('english')           # remove stop words
        clean_jd = [w for w in clean_jd if not w in stop]
        clean_jd = [w for w in clean_jd if not w in other_stop_words]
        return(clean_jd)

def create_word_cloud(jd):
        corpus = jd
        fdist = FreqDist(corpus)
        words = ' '.join(corpus)
        words = words.split()
        data = dict()                               # create a empty dictionary  
        for word in (words):                        #  Get frequency for each words where word is the key and the count is the value   
            word = word.lower()     
            data[word] = data.get(word, 0) + 1 
        dict(sorted(data.items(), key=operator.itemgetter(1),reverse=True)) # Sort the dictionary in reverse order to print first the most used terms
        word_cloud = WordCloud(width = 800, height = 800, 
        background_color ='white',max_words = 500) 
        word_cloud.generate_from_frequencies(data) 

def get_resume_score(text):
        cv = CountVectorizer(stop_words='english')
        count_matrix = cv.fit_transform(text)
        matchPercentage = cosine_similarity(count_matrix)[0][1] * 100       #get the match percentage
        matchPercentage = round(matchPercentage, 2)                         # round to two decimal
        return matchPercentage

def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

def extract_phone_number(resume_text):
    PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
    PHONE_REG2 = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]+\.')

    phone = re.findall(PHONE_REG, resume_text)
    phone2 = re.findall(PHONE_REG2, resume_text)

    if phone:
        number = ''.join(phone[0])

        if resume_text.find(number) >= 0 and len(number) < 16:
            return number
    elif phone2:
        number2 = ''.join(phone2[0])

        if resume_text.find(number2) >= 0 and len(number2) < 16:
            return number2
    else:
        print("Please refer Resume for Contact")

class index(APIView):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]     

    def post(self, request, *args, **kwargs):
        
        #Folder Desitantions
        final_loc = "media/CVs_Parser"
        CV_loc = "media/Resumes"
        destination_folder= "media/Final"
        
        #DB Deletion
        deleting2 = Parser.objects.all()
        deleting2.delete()
        deleting = UploadPdf.objects.all()
        deleting.delete()
        deleting = FinalCV.objects.all()
        deleting.delete()

        #Deletion
        for filename in os.listdir(final_loc):
            file_path = os.path.join(final_loc, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

        for filename in os.listdir(CV_loc):
            file_path = os.path.join(CV_loc, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

        for filename in os.listdir(destination_folder):
            file_path = os.path.join(destination_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

        # print(request.data)
        score_quan = request.data['CV_Num_Input']
        score_perc = request.data['Percent_Input']
        file_JD_1 = request.FILES.getlist('JD_File_Input')
        file2 = request.FILES.getlist('Resumes_File_Input')
        score_dict = {}
        uploading = Parser()

        for i in file_JD_1:
            uploading.file = i
            uploading.save()

        for filename in os.listdir(final_loc):
            print(filename)
            file_path = os.path.join(final_loc, filename)
            job_description = extract_text(file_path)
            print(job_description)
            clean_jd = clean_job_decsription(job_description) 
            create_word_cloud(clean_jd) 

        uploading2 = UploadPdf() #multiple

        for a in file2:
            uploading2 = UploadPdf(resumes=a)
            uploading2.save()
        # os.chdir(CV_loc)
        
        print(os.getcwd())

        for file in os.listdir(CV_loc):
            if file.endswith(".pdf"):
                try:
                    print('Hi')
                    file_path = os.path.join(CV_loc, file)
                    resume = extract_text(file_path).lower()
                    text = [resume, job_description]
                    score_dict[file] = get_resume_score(text)   #get_resume_score(text)
                except:
                    print("PDF ISSUE")
            elif file.endswith(".docx"):
                try:
                    file_path = os.path.join(CV_loc, file)
                    resume = read_word_resume(file_path)
                    text = [resume, job_description]
                    score_dict[file] = get_resume_score(text)   #get_resume_score(text)
                except:
                    print("Docx ISSUE")
            else:
                pass
            # source_folder = CV_loc_1            ##enter location of source folder of cvs
            # # destination_folder = final_loc      ##enter location of destination folder of cvs
        
        i = 100
        msg = []
        msg_email= []
        msg_name = []
        msg_phone= []
        msg_summary = []
        print(score_dict)

        for file_name in heapq.nlargest(int(score_quan), score_dict, key=score_dict.get):   ##change the first attribute to the number of resumes you want to short-list
            print(file_name)
            source = CV_loc + '/' + file_name
            destination = destination_folder + '/' + file_name
            i = i+1
            if os.path.isfile(source):
                print("In here:",file_name)
                shutil.copy(source, destination)
                os.rename(destination, destination_folder + '/'+ str(i) +'_'+ file_name)
                msg.append(file_name)
        
        summarizer = LexRankSummarizer()
        for file in os.listdir(destination_folder):
            if msg[-1].endswith(".pdf"):
                # try:
                file_path = os.path.join(destination_folder, file)
                et = extract_text(file_path)
                et.replace("\n", " ")
                msg_name.append( extract_name1(et))
                msg_email.append(extract_emails(et))
                msg_phone.append(extract_phone_number(et))
                parser=PlaintextParser.from_string(et,Tokenizer("english"))
                summary = summarizer(parser.document,5)
                msg_summary.append(str(summary))
                # except:
                #     print("Issue in Destination PDF")
            elif msg[-1].endswith(".docx"):
                try:
                    file_path = os.path.join(destination_folder, file)
                    ed = read_word_resume(file_path)
                    msg_email.append(extract_emails(ed))
                    msg_phone.append(extract_phone_number(ed))
                    msg_name.append(extract_name1(ed))
                    parser=PlaintextParser.from_string(extract_emails(ed,Tokenizer("english")))
                    summary = summarizer(parser.document,5)
                    msg_summary.append(str(summary))
                except:
                    print("Isuue In Desitantion Docs")
            else:
                print("check cv manually")
        print(msg_name)
        j =0 
        uploading3 = FinalCV() #multiple
        msg_we2 = []
        for a in os.listdir(destination_folder):
            try:
                for i in msg:
                    msg_we = i.split('_')
                    msg_we2.append(msg_we[0])
                # for k in msg_we2:
                #     re.sub(r"(\w)([A-Z])", r"\1 \2", k)
                #     msg_we2.append(k)
                uploading3 = FinalCV(finalcv=a)
                msg_em = msg_email[j]
                uploading3.resume_name = msg_we2[j]
                uploading3.resume_email = msg_em[0]
                uploading3.resume_phone = msg_phone[j]
                uploading3.resume_fname = msg[j]
                uploading3.resume_rank = j+1
                uploading3.resume_summary = msg_summary[j]
                j=j+1
                uploading3.save()
            except:
                print("Issue Uploading3")
        
        get_Mails = FinalCV.objects.all()
        data_cv = FinalSerializer(get_Mails, many=True)

        return Response(data_cv.data, status=status.HTTP_200_OK)   
        #return redirect("http://localhost:3000/parser/Results", status=status.HTTP_200_OK)   

    # def get(self, request, res_mail_js):
    #     get_Mails = FinalCV.objects.get(resume_email = res_mail_js)
    #     return Response({'success':True, 'message': get_Mails.resume_email }, status=status.HTTP_200_OK)

# class CreateModel(viewsets.ModelViewSet):
    
#     def post(self,request):
#         # with transaction.atomic():
#         reg_serializer = ModelSchemasSerializer(data={'name':(request.data)['modelname']})
#         print(request.data)
#         print(reg_serializer.is_valid())
#         if reg_serializer.is_valid():   
#             newmodels = reg_serializer.save()   
#             model_schema = ModelSchema.objects.get(name=(request.data)['modelname'])
            
#             if newmodels:
#                 print("51")
#                 modelname_serializer = List_Database_Serializer(data={'modelname':(request.data)['modelname'], 'description':(request.data)['description'],'color':(request.data)['color'],'icon':(request.data)['icon'],'created_by':NewUser.objects.get(email=(request.data)['created_by']).id})
#                 print("52")
#                 print(modelname_serializer.is_valid())
#                 print(modelname_serializer.errors)
#                 if modelname_serializer.is_valid():
#                     newModelname = modelname_serializer.save()
#                     print("88-done")
#                     if newModelname:
#                         if request.data['group'] != 'self':
#                             link_serializers = CreateList_group_linkSerializer(data={'list':str(newModelname.id),'group':str(Group.objects.get(name=(request.data)['group']).id)})
#                             print(link_serializers.is_valid())
#                             print(link_serializers.errors)
#                             if link_serializers.is_valid():
               
#                                 new_link_model = link_serializers.save()
#                                 if new_link_model:
#                                     register(model_schema)
#                                     reload(import_module(settings.ROOT_URLCONF))
#                                     clear_url_caches()
#                         else:
#                             register(model_schema)
#                             reload(import_module(settings.ROOT_URLCONF))
#                             clear_url_caches()
#                     print("94- life saver done")
#                     ct = ContentType.objects.get_for_model(model_schema.as_model())

#                     Permission.objects.create(codename ='Can_Edit_List',
#                                         name ='Can edit this the list',
#                                         content_type = ct
#                                         )
#                     Permission.objects.create(codename ='Can_Delete_List',
#                                         name ='Can delte this the list',
#                                         content_type = ct
#                                         )
#                     Permission.objects.create(codename ='Can_View_List',
#                                         name ='Can view this the list',
#                                         content_type = ct
#                                         )
#                     Permission.objects.create(codename ='Can_Add_List',
#                                         name ='Can add this the list',
#                                         content_type = ct
#                                         )
#                     LogEntries.objects.create(user = request.user, contenttype = "{} created new list {} in {} group.".format(request.user,(request.data)['modelname'],(request.data)['group']), actionflag = "Create",list=List_Database.objects.get(modelname=(request.data)['modelname']))
#         else:
            
#             return Response(data="List Already exists",status=status.HTTP_400_BAD_REQUEST)
#         try:
#             print(request.data)
#             model_schema = ModelSchema.objects.get(name=request.data['modelname'])
#             #loop    
#             # FIELD_OBJECTS = {"ID":['ID',',] , "Rank": , "Name": , "Email": ,"Phone_No": , "File_name": }  
#             FIELD_OBJECTS = [['ID', FieldFactory.DATA_TYPES['integer'], False, True, FieldFactory.DATA_TYPES['integer'], '', ''],
#                             ['Rank', FieldFactory.DATA_TYPES['integer'], False, True, FieldFactory.DATA_TYPES['integer'], '', ''],
#                             ['Name', FieldFactory.DATA_TYPES['character'], False, True, FieldFactory.DATA_TYPES['character'], '', ''],
#                             ['Email', FieldFactory.DATA_TYPES['character'], True, True, FieldFactory.DATA_TYPES['character'], '', ''],
#                             ['Phone_No', FieldFactory.DATA_TYPES['integer'], True, True, FieldFactory.DATA_TYPES['integer'], '', ''],
#                             ['File_Name', FieldFactory.DATA_TYPES['character'], False, True, FieldFactory.DATA_TYPES['character'], '', '']]
#             for i in FIELD_OBJECTS:
#                 FieldSchema.objects.create(
#                 name= i[0],
#                 data_type=i[1],
#                 model_schema=model_schema,
#                 max_length= 1024,
#                 null=i[2],
#                 unique=i[3],
#                 input_type = i[4],
#                 description = i[5],
#                 columns = i[6],
#                 )
#                 print(request.user)
#                 reregister(model_schema)       
#                 #LogEntries.objects.create(user = request.user, contenttype = "{} Created New Field ( {} ) in {} List.".format(request.user,(request.data)['name'],request.data['modelname']), actionflag = "Create",list=List_Database.objects.get(modelname=request.data['modelname']))

#         except Exception as e:
#             print(e)
#             return Response(data={
#                                 "message": "Fields Cannot Created Check It again.",
#                                     "error": str(e)
#                                                     },status=status.HTTP_400_BAD_REQUEST )
#         return Response("List Sucessfully Created with fields!!!",status=status.HTTP_201_CREATED)

class CreateModels(viewsets.ModelViewSet):
    
    def post(self,request):

        
        # with transaction.atomic():

        reg_serializer = ModelSchemasSerializer(data={'name':(request.data)['modelname']})
        
        print(request.data)
        print(reg_serializer.is_valid())
        
        if reg_serializer.is_valid():
            
            newmodels = reg_serializer.save()
            
            
            model_schema = ModelSchema.objects.get(name=(request.data)['modelname'])
            
            if newmodels:
                print("51")
                modelname_serializer = List_Database_Serializer(data={'modelname':(request.data)['modelname'], 'description':(request.data)['description'],'color':(request.data)['color'],'icon':(request.data)['icon'],'created_by':NewUser.objects.get(email=(request.data)['created_by']).id})
                print("52")
                print(modelname_serializer.is_valid())
                print(modelname_serializer.errors)
                if modelname_serializer.is_valid():
                    newModelname = modelname_serializer.save()
                    print("88-done")
                    if newModelname:
                        ##here error
                        if request.data['group'] != 'self':
                            link_serializers = CreateList_group_linkSerializer(data={'list':str(newModelname.id),'group':str(Group.objects.get(name=(request.data)['group']).id)})
                            print(link_serializers.is_valid())
                            print(link_serializers.errors)
                            if link_serializers.is_valid():
               
                                new_link_model = link_serializers.save()
                                if new_link_model:
                                    register(model_schema)
                                    reload(import_module(settings.ROOT_URLCONF))
                                    clear_url_caches()
                        else:
                            register(model_schema)
                            reload(import_module(settings.ROOT_URLCONF))
                            clear_url_caches()
                    print("94- life saver done")
                    ct = ContentType.objects.get_for_model(model_schema.as_model())

                    Permission.objects.create(codename ='Can_Edit_List',
                                        name ='Can edit this the list',
                                        content_type = ct
                                        )
                    Permission.objects.create(codename ='Can_Delete_List',
                                        name ='Can delte this the list',
                                        content_type = ct
                                        )
                    Permission.objects.create(codename ='Can_View_List',
                                        name ='Can view this the list',
                                        content_type = ct
                                        )
                    Permission.objects.create(codename ='Can_Add_List',
                                        name ='Can add this the list',
                                        content_type = ct
                                        )
                    LogEntries.objects.create(user = request.user, contenttype = "{} created new list {} in {} group.".format(request.user,(request.data)['modelname'],(request.data)['group']), actionflag = "Create",list=List_Database.objects.get(modelname=(request.data)['modelname']))
        
        else:
            
            return Response(data="List Already exists",status=status.HTTP_400_BAD_REQUEST)

        return Response("List Sucessfully Created!!!",status=status.HTTP_201_CREATED)
    
class PassthroughRenderer(renderers.BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
    
  
class FileDownloadListAPIView(generics.ListAPIView):
    
    # def get(self, request, filename, format=None):
    #     queryset = FinalCV.objects.get(id=id)
    #     file_handle = queryset.file.path
    #     document = open(file_handle, 'rb')
    #     response = HttpResponse(FileWrapper(document), content_type='application/msword, application/pdf')
    #     response['Content-Disposition'] = 'attachment; filename="%s"' % queryset.file.name
    #     return response
    # renderer_classes = [PassthroughRenderer]
    def get(self, request, filename): 
  
        file = FinalCV.objects.get(resume_fname = filename) 
        name1 = str(file.finalcv.path).split('media')
        name2 = name1[0] + 'media\\Final' + name1[1]
        print(name2)
        print(os.path.getsize(name2))
        file_handle = open( name2, 'rb')
        # print(file_handle)   
        mimetype, _ = mimetypes.guess_type(file.resume_fname)
        print(mimetype)
        response = FileResponse(file_handle, content_type=mimetype)
        response['Content-Length'] = os.path.getsize(name2)
        response['Content-Disposition'] = "attachment; filename={}".format(file.resume_fname)
        response['accepted_media_type'] = mimetype
        return response
        
