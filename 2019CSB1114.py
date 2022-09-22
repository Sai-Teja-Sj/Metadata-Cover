import argparse
import cv2
import pandas as pd
from pytesseract import *
import numpy as np
import re
import math
import os
import spacy
import csv
import openpyxl
header=['title', 'Author', 'ISBN','Publisher']
pd.set_option('display.max_columns', None)

ap=argparse.ArgumentParser()
ap.add_argument("-a", "--az", type=str,required= True, help="path to Book dataset")
#ap.add_argument("-m", "--model", type=str, required=True, help="path to tesseract exec")
ap.add_argument("-f","--flag",type=str, default=1, help="option to choose the file or directory")
ap.add_argument("-file","--file", type=str, help="path to files or folder")
args=vars(ap.parse_args())


print("INFO loading datasets..")
file_name=os.path.abspath(args['az'])
if os.path.isfile(file_name) is False:
    print(file_name)
    print('Cannot open dataset quitting....')
    exit()
else :
    print("exists")    
data=pd.read_csv(args["az"])
pytesseract.tesseract_cmd=r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class bounding_boxes:
    def get_bounding_boxes(images):
        rgb=cv2.cvtColor(images,cv2.COLOR_BGR2RGB)
        ##grayscale 
        img=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        #cv2.imshow("sidfubu",img)
    

        #cv2.waitKey(0)
        results= pytesseract.image_to_data(img,output_type='data.frame')
        return results


    def give_distance(i,j,results): 
        if results["block_num"][j] == results["block_num"][i]  and results["word_num"][i] > results["word_num"][j] and results["line_num"][j] == results["line_num"][i]:
            if ((results["height"][i] - results["height"][j] <=4) or (results["height"][j] - results["height"][i] <=4)): #or results["height"][i] - results["height"][j] <= -4 or results["height"][i] - results["height"][j] >=-4:
                str=[]
                return (int (results["left"][i] -(results["width"][j]+ results["left"][j]) ))

                #str.append( (results["height"][i] - results["height"][j]))
                #strr=[]
                #strr.append(str)
                #return strr
            else:
                return None
        else:
            return None  
    def compute_area(results):
        area=[]
        for i in range(0,len(results["text"])):
            area.append(int (results["height"][i]) * int(results["width"][i]))
        return area

    def detect_and_draw(results,images):
        for i in range(0,len(results["text"])):
            x=results["left"][i]
            y=results["top"][i]
            w=results["width"][i]
            h=results["height"][i]
            text=results["text"][i]
            l=results["line_num"][i]
            conf1=results["conf"][i]
            conf=float(conf1)
            if conf >0.0 and results["conf"][i]!=-1 :
                text="".join(text).strip()
                cv2.rectangle(images,(x,y),(x+w,y+h),(0,0,255),2)
            #cv2.rectangle(imag,(x,y),(x+w,y+h),(0,0,255),2)
            #cv2.putText(images, text,(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,1.2,(0,255,255),3)

        return images 

    def get_block(self, results):
        string=""
        str=[]
        for i in range(0,len(results)):
            if i>0:
                dis= self.give_distance(i,i-1,results)
                if dis is not None and dis <80:
                    string = string +  results["text"][i-1] + " "

                elif dis is None or dis >80:
                    string = string + results["text"][i-1] + " "
                    str.append(string)
                    string =""   
                if i == len(results)-1:
                    string = string + results["text"][i] + " "
                    str.append(string)
                    string =""


        return str                 


    def findisbn(results):
        regex='.ISBN[\-|\s]?[13|10]?\s[0-9]{3}\-[0-9]\-[0-9]{2}\-[0-9]{6}\-[0-9]$'
        regex1='.*ISBN.*'
        regex2='^(?:ISBN(?:-13)?:?\ )?(?=[0-9]{13}$|(?=(?:[0-9]+[-\ ]){4})[-\ 0-9]{17}$)97[89][-\ ]?[0-9]{1,5}[-\ ]?[0-9]+[-\ ]?[0-9]+[-\ ]?[0-9]$'
        for i in range(0,len(results)):
            x=re.match(regex2,results[i])
            y=re.match(regex1,results[i])
            w=re.match(regex,results[i])
            #print(results[i])
            if x is not None  or y is not None  or w is not None  :
                #if results[i].find("ISBN")!=-1:
                sample=re.split(regex2,results[i])
                return results[i]
            else:
                continue       
        return None 
    
    def find_publisher(results):
        regex='.*Copyright.*by*'
        for i in range(0,len(results)):
            x=re.match(regex,results[i])
            if x is not None:
                sample=re.split(regex,results[i])
                #print(sample)
                if sample[-1].count('.')==0:
                    y=results[i+1]
                    sample2=y.split(".")
                    y=sample[-1]+sample2[0]
                    return y
                elif sample[-1].count('.') >0:
                    sample2=results[i].split('.')
                    y=sample2[0]

                    return y


                return results[i]
        #print("No copyright sign")
        regex='.*please[\s+]?contact.*'
    
        return None


    def title(results1, line_conf):
        for i in range(0,len(results1["area"])):
            if re.match("\w+",results1["text"][i]) is not None and (results1["text"][i]!=""):
                if re.match("(\w| \, |.)+",results1["text"][i]) is not None:
                    for j in range(0,len(line_conf)):
                        if line_conf[j][0].find(results1["text"][i]) !=-1:
                            title=line_conf[j][0]
                            return title 

        return ""  

    def total_text(str):
        string =""
        for i in range(len(str)):
            string = string + str[i]

        return string     
    def author(string,str):
        english_nlp=spacy.load('en_core_web_sm')
        spacy_parser= english_nlp(string)
        names=[]
        for i in range(len(str)):
            spacy_parser=english_nlp(str[i])
            for entity in spacy_parser.ents:
                if entity.label_ == "PERSON":
                    names.append(entity.text)

        df=pd.DataFrame({"name": names})
        v=df.mode()["name"]
        m=""
        for i in range(len(v)):
            if len(v[i]) >len (m):
                m=v[i]
        return m                
class file:
    def writing_headers():
        with open('output.csv', 'a', newline='') as csvfile:
            csvwriter=csv.writer(csvfile)
            
            csvwriter.writerow(header)

    def check_file(file_path):
        #print("checkign files")
        filelist=[]
        for root, dirs, files in os.walk(file_path):
            for file in files:
                filelist.append(os.path.join(root,file)) 

        return filelist 



class initiate:
    def processing(image_path):
        if args["flag"] =='1' or args["flag"] =='0':
            images=cv2.imread(image_path)
            (H,W)=images.shape[:2]
            results=bounding_boxes.get_bounding_boxes(images)
            images=bounding_boxes.detect_and_draw(results,images)
            img=images  #creating object
            results1=results
            area=bounding_boxes.compute_area(results)
            #cv2.imshow("dsjvd",images)
            #cv2.waitKey(0)
            results1["area"]=area
            results= results.dropna().reset_index(drop=True)


            lines=results.groupby(["page_num", "block_num", "par_num", "line_num",])["text"]\
                                                    .apply(lambda x: " ".join(list(x))).tolist()
            #print(lines)
            confs=results.groupby(["page_num", "block_num", "par_num", "line_num"])["conf"].mean().tolist()
            areas=results.groupby(["page_num", "block_num", "par_num", "line_num"])["conf"].mean().tolist()
            line_conf = []
            #print(lines)    
            for i in range(len(lines)):
                if lines[i].strip():
                    line_conf.append((lines[i], round(confs[i],3)))

            #print("sdfubofif",line_conf)    
            #cv2.imshow("Image",images)
            #cv2.waitKey(0)  
            lines1=lines#results.groupby(["page_num", "block_num", "par_num", "line_num",])["text"] .apply(lambda x: " ".join(list(x))).tolist()
            #print(lines)
            max= results.max(skipna= False)
            str=bounding_boxes.get_block(bounding_boxes,results)
            #print(str)

            results1= results1.dropna().reset_index(drop=True)
            results1=results1.sort_values("area", axis=0,ascending = False)
            results1=results1.reset_index(drop=True)
            min =0                
            title1=bounding_boxes.title(results1,line_conf)
            print("title:",title1) #title(results1, line_conf))
            #print(lines1)
            #print(lines)
            isbn_value= bounding_boxes.findisbn(str)
            isbn=isbn_value.replace("ISBN","")
            isbn=isbn.replace(" ",'')
            isbn=isbn.replace("-",'')
            print("ISBN:", isbn)
            publi=bounding_boxes.find_publisher(str)

            print("Publishers:",publi )
            string =bounding_boxes.total_text(str)
            m=bounding_boxes.author(string, str)
            print("Author:",m)
            res=[]
            res.append(title1)
            res.append(m)
            res.append(isbn)
            res.append(publi)
            with open('output.csv', 'a', newline='') as csvfile:
                csvwriter=csv.writer(csvfile)
            
                csvwriter.writerow(res)

            resu=[]
            resu.append(resu)
            '''path='output.xlsx'
            df=pd.DataFrame({'Title':[title1],'Author Name':[m],'ISBN':[isbn],'Publisher':[publi]})
            if os.path.exists('output.xlsx'):
                with pd.ExcelWriter(path) as writer:
                    writer.book = openpyxl.load_Workbook(path)
                    df.to_excel(writer)
                    #df2.to_excel(writer, sheet_name='new_sheet2')

            else:
                df.to_excel('./output.xlsx')  ''' 
            return resu

if args["flag"]=='1':
    resu=initiate.processing(args["file"])
    print(resu)
if args["flag"]=='0':
    filelist=file.check_file(args["file"])
    print(filelist)  
    for i in range(len(filelist)):
        resu=initiate.processing(filelist[i])
        print(resu)  























    
    
    


