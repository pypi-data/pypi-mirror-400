import cv2
import pandas as pd
import numpy as np
widthImg=800
heightImg=800
RectangleScore_dict={}
DisplayLocation={'Roll':1,'TF':2,'QA':3}
DisplayLocation_3img={'Roll':0,'TF':1,'QA':2}

#Rectangle_Shape_Dict={'QA':(14,8),'TF':(5,10),'Roll':(8,10)}
#Rectangle_Shape_Dict={'QA':(14,9),'TF':(11,4),'Roll':(11,7)}
Rectangle_Shape_Dict={'QA':(14,9),'TF':(12,4),'Roll':(11,7)}

T='T';F='F';
a, b, c, d, e, f = 'a', 'b', 'c', 'd', 'e', 'f'


Rectangle_no_dict={'QA':0,'Roll':1,'TF':2}


def imgPreProcess(img, widthImg, heightImg,rectContours,TakeRectangle,threshold_value=0.5):
    #imgCanny = getImgCanny(img)
    # imgBlank = np.zeros_like(img)
    # contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #rectContours, imgContours = getRectangles_fromImage(img, widthImg, heightImg)

    rectangle_no=Rectangle_no_dict[TakeRectangle]
    selectedContour = getCornerPoints(rectContours[rectangle_no])

    imgWarpColored = getWarpPerspective(img, selectedContour, widthImg, heightImg)
    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)


    # if threshold_value is None:
    #     threshold_value=(int(imgWarpGray.min())+int(imgWarpGray.max()))/2
    # else:
    threshold_value=int(imgWarpGray.min()*threshold_value)+int(imgWarpGray.max()*(1-threshold_value))

    imgThreshold = cv2.threshold(imgWarpGray, threshold_value, 255, cv2.THRESH_BINARY_INV)[1]
    return imgThreshold,imgWarpColored

def getWarpPerspective(img,selectedContour,widthImg,heightImg):
    selectedContour = reorder(selectedContour)
    pt1 = np.float32(selectedContour)
    pt2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
    matrix = cv2.getPerspectiveTransform(pt1, pt2)
    # Transform the image into bird-eye-view using the warp transformation matrix
    imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
    return imgWarpColored

def getRectangles_fromImage(img,widthImg, heightImg):
    img = cv2.resize(img, (widthImg, heightImg))
    imgContours = img.copy()

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur, 10, 50)  # Canny is edge detector. Here we are able to detect the edge of the rectengles

    ##### FINDING ALL CONTOURS
    contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # Draw all the contours with green line

    #### FIND RECTANGLES
    rectContours = rectContour(contours)  # Find the rectangular contours and sort them according to their area
    return rectContours,imgContours

def rectContour(contours):
    rectCon=[]
    for i in contours:
        area=cv2.contourArea(i)
        #print(area)
        if area>50:
            perimeter=cv2.arcLength(i,True) #Closed perimeter=True
            approx=cv2.approxPolyDP(i,0.02*perimeter,True) #Finds the number of corner points
            #print("Corner Points",len(approx))
            if len(approx)==4:  #taking the rectangles only
                rectCon.append(i)
    rectCon=sorted(rectCon,key=cv2.contourArea,reverse=True)
    return rectCon

def reorder(myPoints):
    #This function takes the corner points of a rectangle as input.
    # Then x+y=minimu, its the origin. If x+y=maximum, it is (w,h)
    #If x-y is minimum, it is (0,h). if x-y is maximu, it is the remaining point (h,0)

    myPoints=myPoints.reshape((4,2))
    myPointsNew_likeVideo=np.zeros((4,1,2),np.int32)
    add=myPoints.sum(1) #

    myPointsNew_likeVideo[0]=myPoints[np.argmin(add)]  #[0,0]
    myPointsNew_likeVideo[3]=myPoints[np.argmax(add)]  #[w,h]
    diff=np.diff(myPoints,axis=1)
    myPointsNew_likeVideo[1]=myPoints[np.argmin(diff)]  #[w,0]
    myPointsNew_likeVideo[2]=myPoints[np.argmax(diff)]  #[0,h]
    return myPointsNew_likeVideo
def getCornerPoints(contour):
    perimeter = cv2.arcLength(contour, True)  # Closed perimeter=True
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter,True)  # Finds the number of corner points
    return approx


def getImgCanny(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur, 10,50)  # Canny is edge detector. Here we are able to detect the edge of the rectengles
    return imgCanny


def fillFraction(box):
    n_pixel=cv2.countNonZero(box)
    total_pixel=np.shape(box)[0]*np.shape(box)[1]
    return round(n_pixel / total_pixel,4)

def get_Fillups(imgThreshold,n_rows,n_cols,n_skipPixels=30,w=0.5):
    # This function splits a rectangle into individual boxes. Then calculates box fill fraction
    # Note that sometimes box can be significantly larger than the OMR circle. In that case we skip few pixels along
    # the horizontal direction. In other words, we crop the image horizontally
    imgThreshold_modified = cv2.resize(imgThreshold, (n_cols * 100, n_rows * 100))
    rows = np.vsplit(imgThreshold_modified, n_rows)
    ############################
    boxes=[]
    rgbBoxes=[]
    boxFillFractions=[]
    for row in rows:
        cols=np.hsplit(row, n_cols)
        for box in cols:
            grayBox = box.copy()
            rgb_box = cv2.cvtColor(grayBox, cv2.COLOR_GRAY2RGB)

            box=box[:,n_skipPixels:100-n_skipPixels]
            boxes.append(box)
            fill = fillFraction(box)
            boxFillFractions.append(fill)
            #Mark the cropped region with "Blue gray"
            rgb_box[:, 0:n_skipPixels, 1] = 54;rgb_box[:, -n_skipPixels:, 1] = 54
            rgb_box[:, 0:n_skipPixels, 1] = 147;rgb_box[:, -n_skipPixels:, 1] = 147
            rgb_box[:, 0:n_skipPixels, 2] = 179;rgb_box[:, -n_skipPixels:, 2] = 179
            rgbBoxes.append(rgb_box)

    boxes = np.reshape(boxes, (n_rows, n_cols, np.shape(boxes)[1], np.shape(boxes)[2]))
    rgbBoxes=np.reshape(rgbBoxes,(n_rows, n_cols, np.shape(rgbBoxes)[1], np.shape(rgbBoxes)[2],np.shape(rgbBoxes)[3]))
    boxFillFractions = np.reshape(boxFillFractions, (n_rows, n_cols))


    # threshold_row=boxFillFractions[0,:]
    # threshold=w*threshold_row.max()+(1-w)*threshold_row.min()
    threshold=w*boxFillFractions.max()+(1-w)*boxFillFractions.min()

    ind=np.where(boxFillFractions>threshold)
    fillupMatrix=np.zeros(np.shape(boxFillFractions))
    fillupMatrix[ind]=1

    return boxes,rgbBoxes,boxFillFractions,fillupMatrix





#answer_loc_dict={'a':1, 'b':2, 'c':4, 'd':5, 'e':7, 'f':8}

answer_loc_dict={'a':1, 'b':2, 'c':4, 'd':5, 'e':7, 'f':8,'T':1,'F':3}

def GenerateCorrectAnswerMatrix(Correct_answer_dict,Rectangle_Shape,ignore_nrows=2):

    correct_answer_matrix = np.zeros(Rectangle_Shape)
    for key in Correct_answer_dict:
        correct_answer=Correct_answer_dict[key]  #a, b, c etc.
        column=answer_loc_dict[correct_answer]
        #print(key,column)
        correct_answer_matrix[int(key)+int(ignore_nrows-1), column] = 1
    return correct_answer_matrix




def RotateClockwise(*Matrices):
    retList=[]
    for matrix in Matrices:
        matrix=cv2.rotate(matrix, cv2.ROTATE_90_CLOCKWISE)
        retList.append(matrix)
    return retList




def Nullify_DoubleAnswers(fillups,TakeRectangle):
    def ApplyNullification(fillups_innder):
        fillupNullified = fillups_innder.copy()
        for nn in range(0, np.shape(fillups)[0]):
            ind = np.where(fillups[nn,] == 1)
            if len(ind[0])> 1:
                fillupNullified[nn,ind]='Nan'
        return fillupNullified

    fillups[0, :] = 0
    if TakeRectangle=='TF':
        fillupProcessed=ApplyNullification(fillups)
    elif TakeRectangle=='QA':
        if np.shape(fillups)[0]<np.shape(fillups)[1]:
            print("Nullify_DoubleAnswers: Wrong fillup matrix supplied!!! Expecting for 'QA' box...")
            #print(colored("Nullify_DoubleAnswers: Wrong fillup matrix supplied!!! Expecting for 'QA' box..."),'red')
        fillupProcessed = ApplyNullification(fillups)
    else:
        fillupProcessed = ApplyNullification(fillups)
        # fillups[0, :] = 'Nan'
        # fillupProcessed=fillups
    return  fillupProcessed



def computeRoll(fillupMatrix,TakeRectangle):
    fillupMatrix=fillupMatrix[1:,:]  #Skipping 1st row

    if TakeRectangle=='Roll':
        roll=0
        for nn in range(0,7):
            col=fillupMatrix[:,nn]
            ind=np.where(col==1)[0]
            if len(ind)==0:
                print("Roll: No fillup in col ",nn,'\t',col)
                return -1
            elif len(ind)>1:
                print("Roll: Multiple fillup in col ",nn,'\t',col)
                return -1
            else:
                roll=roll+10**(6-nn)*ind[0]
    else:
        roll=-1
    return '{:07.0f}'.format(roll)

def computeRoll_v2(boxFillFractions,TakeRectangle,ignore_nrows=2,w=0.5):
    n_cols=np.shape(boxFillFractions)[1]
    fillupMatrix=np.zeros(np.shape(boxFillFractions))

    threshold=w*boxFillFractions[0,:].max()+(1-w)*boxFillFractions[0,:].min()
    ind=np.where(boxFillFractions[0,:]>threshold)
    fillupMatrix[0,ind]=1

    for nn in range(n_cols):
        ind=np.where(boxFillFractions[ignore_nrows:,nn]==max(boxFillFractions[ignore_nrows:,nn]))[0]
        fillupMatrix[ind+ignore_nrows,nn]=1  #Skipping 1st "ignore_nrows"


    if TakeRectangle=='Roll':
        roll=0
        for nn in range(0,7):
            col=fillupMatrix[ignore_nrows:,nn]
            ind=np.where(col==1)[0]
            if len(ind)==0:
                print("Roll: No fillup in col ",nn,'\t',col)
                return -1
            elif len(ind)>1:
                print("Roll: Multiple fillup in col ",nn,'\t',col)
                return -1
            else:
                roll=roll+10**(6-nn)*ind[0]
    else:
        roll=-1

    return fillupMatrix,'{:07.0f}'.format(roll)



import itertools

def showRoll(imgWarpColored, fillupMatrix_doubleAns_nullified):
    imgAnswers = imgWarpColored.copy()

    n_rows = np.shape(fillupMatrix_doubleAns_nullified)[0]
    n_cols = np.shape(fillupMatrix_doubleAns_nullified)[1]


    secW = int(imgAnswers.shape[1] / n_cols)
    secH = int(imgAnswers.shape[0] / n_rows)
    thickness = 8

    for row, col in itertools.product(range(1,n_rows), range(n_cols)):
        if np.isnan(fillupMatrix_doubleAns_nullified[row,]).any():  # If row contains a 'nan' (multiple answer),continue
            cX=int(secW / 2 + 0 * secW)
            cY = int(secH / 2 + row * secH)
            cv2.rectangle(imgAnswers, (int(cX - secW / 2), int(cY+ secH / 2)),
                          (int(cX+n_rows* secW + secW / 2), int(cY - secH / 2)), (94, 48, 201), thickness)
            continue

        Entry_Student_answerMatrix = fillupMatrix_doubleAns_nullified[row, col]

        if Entry_Student_answerMatrix:   #Mark the answer only if student answered it
            cX_student = int(secW / 2 + col * secW)
            cY_student = int(secH / 2 + row * secH)

            cv2.rectangle(imgAnswers, (int(cX_student-secW / 2),int(cY_student+secH/2)), (int(cX_student+secW / 2),int(cY_student-secH/2)), (255, 255, 0), thickness)
    return imgAnswers






def Convert_integer_mark_into_dictionary(Mark_correctAns_dict,Mark_wrongAns_dict,dictLen):
    if type(Mark_correctAns_dict) is not dict:
        tmp_Mark_correctAnswer = {}
        tmr_Mark_wrongAnswer = {}
        for row in range(0, dictLen):
            tmp_Mark_correctAnswer[row] = Mark_correctAns_dict
            tmr_Mark_wrongAnswer[row] = Mark_wrongAns_dict
        Mark_correctAns_dict = tmp_Mark_correctAnswer
        Mark_wrongAns_dict = tmr_Mark_wrongAnswer
    return Mark_correctAns_dict,Mark_wrongAns_dict


def GenerateScore(TakeRectangle,Mark_dict,correct_answer_matrix,fillupMatrix_doubleAns_nullified,imgWarpColored,ignore_nrows=2):
    def _GenerateScore(correct_answer_matrix,fillupMatrix_doubleAns_nullified,Mark_correctAnswer_dict,Mark_wrongAnswer_dict,imgWarpColored,ignore_nrows):
        n_rows = np.shape(correct_answer_matrix)[0]
        n_cols = np.shape(correct_answer_matrix)[1]

        text_x_offset_dict = {'TF': 2, 'QA': 4}
        mark_x_offset_dict = {'TF': 0.6, 'QA': 3}
        text_x_offset = text_x_offset_dict[TakeRectangle]
        mark_x_offset_dict = mark_x_offset_dict[TakeRectangle]
        imgAnswers = imgWarpColored.copy()
        secW = int(imgAnswers.shape[1] / n_cols)
        secH = int(imgAnswers.shape[0] / n_rows)
        angle = 0;
        startAngle = 0;
        endAngle = 360;
        axesLength = (int(secW / 2.5), int(secH / 2));
        thickness = 8

        score_positive = 0
        score_negative = 0

        for row in range(ignore_nrows, n_rows):
            # if Mark_correctAnswer is None or Mark_wrongAnswer is None:  #If the mark is not given
            #     continue

            Row_studentAnswerMatrix = fillupMatrix_doubleAns_nullified[row, :]
            Row_CorrectAnswerMatrix = correct_answer_matrix[row, :]
            Dict_key = row - (ignore_nrows - 1)

            if not np.any(Row_studentAnswerMatrix):  #Student did not answer this question.
                continue
            if np.isnan(Row_studentAnswerMatrix).any():  # Multiple answering nullifies the answer.
                cX = int(secW / 2 + 0 * secW)
                cY = int(secH / 2 + row * secH)
                cv2.rectangle(imgAnswers, (int(cX - secW / 2), int(cY + secH / 2)),(int(cX + n_rows * secW + secW / 2), int(cY - secH / 2)), (94, 48, 201), thickness)
                text_coordinate = (int(secW * text_x_offset), cY)
                cv2.putText(imgAnswers, "Null", text_coordinate, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4, cv2.LINE_AA)
                continue


            studentAnsIndex = np.where(Row_studentAnswerMatrix == 1)[0]
            correctAnsIndex = np.where(Row_CorrectAnswerMatrix == 1)[0]

            cX_student = int(secW / 2 + studentAnsIndex * secW)
            cY_student = int(secH / 2 + row * secH)
            student_fillup_coordinate = (cX_student, cY_student);
            Mark_text_coordinate = (int(secW * mark_x_offset_dict), cY_student)
            #        Mark_text_coordinate=(int(secW / 2), cY_student)
            text_coordinate = (int(secW * text_x_offset), cY_student)


#            print(TakeRectangle,"Mark=",Mark_correctAnswer_dict)

            if not np.any(Row_CorrectAnswerMatrix):  # If there is no "correct answer" of a given question, though student answered it.
                                                     # In that case, assume this question does not exist, and continue.
                cv2.rectangle(imgAnswers, (int(cX_student-secW / 2),int(cY_student+secH/2)), (int(cX_student+secW / 2),int(cY_student-secH/2)), (255, 255, 0), thickness)
                cv2.putText(imgAnswers,"Ans. Not Provided",text_coordinate,cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),4,cv2.LINE_AA)
                continue



            elif studentAnsIndex == correctAnsIndex:    #Student filled the correct circle
                cv2.ellipse(imgAnswers, student_fillup_coordinate, axesLength, angle, startAngle, endAngle, (0, 255, 0),thickness)
                if Mark_correctAnswer_dict.get(Dict_key) is not None and not np.isnan(Mark_correctAnswer_dict.get(Dict_key)):
                    Mark_correctAnswer = Mark_correctAnswer_dict.get(Dict_key)
                    score_positive = score_positive + Mark_correctAnswer
                    cv2.putText(imgAnswers,str(Mark_correctAnswer),Mark_text_coordinate,cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),4,cv2.LINE_AA)
                else:
                    cv2.putText(imgAnswers, "CA Mark Not provided", text_coordinate, cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 255), 4,cv2.LINE_AA)


            else: #student filled a wrong circle
                cv2.ellipse(imgAnswers, student_fillup_coordinate, axesLength, angle, startAngle, endAngle, (0, 0, 255),thickness)
                col = np.where(correct_answer_matrix[row,] == 1)[0]
                cX_correct = int(secW / 2 + col * secW); cY_correct = int(secH / 2 + row * secH)
                cv2.ellipse(imgAnswers, (cX_correct, cY_correct), axesLength, angle, startAngle, endAngle, (255, 255, 0), thickness)

                if Mark_wrongAnswer_dict.get(Dict_key) is not None and not np.isnan(Mark_wrongAnswer_dict.get(Dict_key)):
                    Mark_wrongAnswer = Mark_wrongAnswer_dict.get(Dict_key)
                    score_negative = score_negative + Mark_wrongAnswer
                    cv2.putText(imgAnswers,str(Mark_wrongAnswer),Mark_text_coordinate,cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),4,cv2.LINE_AA)
                else:
                    cv2.putText(imgAnswers, "WA Mark Not provided", text_coordinate, cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 255), 4, cv2.LINE_AA)

        return score_positive,score_negative,imgAnswers
    ##################################  showAnswers  works from Here ###############################################


    Mark_correctAnswer_dict,Mark_wrongAnswer_dict=Mark_dict[TakeRectangle]
    dictLen=np.shape(correct_answer_matrix)[0]
    Mark_correctAnswer_dict, Mark_wrongAnswer_dict = Convert_integer_mark_into_dictionary(Mark_correctAnswer_dict,Mark_wrongAnswer_dict,dictLen)

    score_positive,score_negative,imgAnswers=_GenerateScore(correct_answer_matrix,fillupMatrix_doubleAns_nullified,Mark_correctAnswer_dict, Mark_wrongAnswer_dict,imgWarpColored,ignore_nrows)

    return score_positive,score_negative,imgAnswers



def Conv_FirstRow_into_Binary(a):
    b = 0
    for i in range(len(a)):
        b=b+10**i*a[len(a)-i-1]
    return int(b)

def ReadCorrectAnswer(xlsxFN, nrows=12, usecols='A:Q', Print=False):
    print("\n\t\tReading "+str(xlsxFN)+'...')
    AllAnswer_df = pd.read_excel(xlsxFN, nrows=nrows, usecols=usecols)

    TF_df = AllAnswer_df[
        ['True/False no', 'T/F Set 1', 'T/F Set 2', 'T/F Set 3', 'Correct T/F mark', 'Wrong T/F mark']].copy()
    QA_df = AllAnswer_df[
        ['Question no', 'Q/A Set 1', 'Q/A Set 2', 'Q/A Set 3', 'Correct Q/A mark', 'Wrong Q/A mark']].copy()

    Course = list(AllAnswer_df['Course'])[0]

    binaryCode=AllAnswer_df['Binary code'].dropna()
    binaryCode=list(binaryCode.astype(int))
    equivalentSetCode=AllAnswer_df['Equivalent Set Code'].dropna()
    equivalentSetCode =list(equivalentSetCode.astype(int))
    SetCode = pd.Series(equivalentSetCode,index=binaryCode)
    GetSetCode_from_Binary=SetCode.to_dict()


#    TF_df = TF_df.dropna(subset=['T/F Set 1', 'T/F Set 2', 'T/F Set 3', 'Correct T/F mark', 'Wrong T/F mark'])
#    QA_df = QA_df.dropna(subset=['Q/A Set 1', 'Q/A Set 2', 'Q/A Set 3', 'Correct Q/A mark', 'Wrong Q/A mark'])

    if Print:
        print('\n\t Verify the content of '+str(xlsxFN)+':\n')
        print('\t\tCourse= ',Course)
        for key in GetSetCode_from_Binary:
            print("\t\tBinary:", key, '\t\tSet Code:', GetSetCode_from_Binary[key])
        print('\n')
        print(TF_df.to_string(index=False), '\n', QA_df.to_string(index=False))

    TF_question_no = TF_df['True/False no']
    TF_set1 = TF_df['T/F Set 1']
    TF_set2 = TF_df['T/F Set 2']
    TF_set3 = TF_df['T/F Set 3']
    C_TF_Mark_Arr = TF_df['Correct T/F mark']
    W_TF_Mark_Arr = TF_df['Wrong T/F mark']

    QA_question_no = QA_df['Question no']
    QA_set1 = QA_df['Q/A Set 1']
    QA_set2 = QA_df['Q/A Set 2']
    QA_set3 = QA_df['Q/A Set 3']
    C_QA_Mark_Arr = QA_df['Correct Q/A mark']
    W_QA_Mark_Arr = QA_df['Wrong Q/A mark']


    
    TF_ind_set1={}
    TF_ind_set2 = {}
    TF_ind_set3 = {}
    Mark_correctAnswer_TF={}
    Mark_wrongAnswer_TF={}


    for i in range(len(TF_question_no)):
        if isinstance(TF_set1[i], str):
            TF_ind_set1[TF_question_no[i]] = TF_set1[i].strip()
        if isinstance(TF_set2[i], str):
            TF_ind_set2[TF_question_no[i]] = TF_set2[i].strip()
        if isinstance(TF_set3[i], str):
            TF_ind_set3[TF_question_no[i]] = TF_set3[i].strip()
        Mark_correctAnswer_TF[TF_question_no[i]] = C_TF_Mark_Arr[i]
        Mark_wrongAnswer_TF[TF_question_no[i]] = W_TF_Mark_Arr[i]

    QA_ind_set1={}
    QA_ind_set2 = {}
    QA_ind_set3 = {}
    Mark_CorrectAnswer_QA={}
    Mark_wrongAnswer_QA={}

    for i in range(len(QA_question_no)):
        if isinstance(QA_set1[i], str):
            QA_ind_set1[QA_question_no[i]] = QA_set1[i].strip()
        if isinstance(QA_set2[i], str):
            QA_ind_set2[QA_question_no[i]] = QA_set2[i].strip()
        if isinstance(QA_set3[i], str):
            QA_ind_set3[QA_question_no[i]] = QA_set3[i].strip()
        Mark_CorrectAnswer_QA[QA_question_no[i]] = C_QA_Mark_Arr[i]
        Mark_wrongAnswer_QA[QA_question_no[i]] = W_QA_Mark_Arr[i]

    return Course,GetSetCode_from_Binary,TF_ind_set1, TF_ind_set2, TF_ind_set3, QA_ind_set1, QA_ind_set2, QA_ind_set3, Mark_correctAnswer_TF, Mark_wrongAnswer_TF, Mark_CorrectAnswer_QA, Mark_wrongAnswer_QA


def ReadCorrectAnswer_dict_from_webread_df(AllAnswer_df, Print=False):

    TF_df = AllAnswer_df[
        ['True/False no', 'T/F Set 1', 'T/F Set 2', 'T/F Set 3', 'Correct T/F mark', 'Wrong T/F mark']].copy()
    QA_df = AllAnswer_df[
        ['Question no', 'Q/A Set 1', 'Q/A Set 2', 'Q/A Set 3', 'Correct Q/A mark', 'Wrong Q/A mark']].copy()

    Course = list(AllAnswer_df['Course'])[0]

    binaryCode=AllAnswer_df['Binary code'].dropna()
    binaryCode=list(binaryCode.astype(int))
    equivalentSetCode=AllAnswer_df['Equivalent Set Code'].dropna()
    equivalentSetCode =list(equivalentSetCode.astype(int))
    SetCode = pd.Series(equivalentSetCode,index=binaryCode)
    GetSetCode_from_Binary=SetCode.to_dict()


#    TF_df = TF_df.dropna(subset=['T/F Set 1', 'T/F Set 2', 'T/F Set 3', 'Correct T/F mark', 'Wrong T/F mark'])
#    QA_df = QA_df.dropna(subset=['Q/A Set 1', 'Q/A Set 2', 'Q/A Set 3', 'Correct Q/A mark', 'Wrong Q/A mark'])

    if Print:
        print('\n\t Verify the content of '+str(xlsxFN)+':\n')
        print('\t\tCourse= ',Course)
        for key in GetSetCode_from_Binary:
            print("\t\tBinary:", key, '\t\tSet Code:', GetSetCode_from_Binary[key])
        print('\n')
        print(TF_df.to_string(index=False), '\n', QA_df.to_string(index=False))

    TF_question_no = TF_df['True/False no']
    TF_set1 = TF_df['T/F Set 1']
    TF_set2 = TF_df['T/F Set 2']
    TF_set3 = TF_df['T/F Set 3']
    C_TF_Mark_Arr = TF_df['Correct T/F mark']
    W_TF_Mark_Arr = TF_df['Wrong T/F mark']

    QA_question_no = QA_df['Question no']
    QA_set1 = QA_df['Q/A Set 1']
    QA_set2 = QA_df['Q/A Set 2']
    QA_set3 = QA_df['Q/A Set 3']
    C_QA_Mark_Arr = QA_df['Correct Q/A mark']
    W_QA_Mark_Arr = QA_df['Wrong Q/A mark']


    
    TF_ind_set1={}
    TF_ind_set2 = {}
    TF_ind_set3 = {}
    Mark_correctAnswer_TF={}
    Mark_wrongAnswer_TF={}


    for i in range(len(TF_question_no)):
        if isinstance(TF_set1[i], str):
            TF_ind_set1[TF_question_no[i]] = TF_set1[i].strip()
        if isinstance(TF_set2[i], str):
            TF_ind_set2[TF_question_no[i]] = TF_set2[i].strip()
        if isinstance(TF_set3[i], str):
            TF_ind_set3[TF_question_no[i]] = TF_set3[i].strip()
        Mark_correctAnswer_TF[TF_question_no[i]] = C_TF_Mark_Arr[i]
        Mark_wrongAnswer_TF[TF_question_no[i]] = W_TF_Mark_Arr[i]

    QA_ind_set1={}
    QA_ind_set2 = {}
    QA_ind_set3 = {}
    Mark_CorrectAnswer_QA={}
    Mark_wrongAnswer_QA={}

    for i in range(len(QA_question_no)):
        if isinstance(QA_set1[i], str):
            QA_ind_set1[QA_question_no[i]] = QA_set1[i].strip()
        if isinstance(QA_set2[i], str):
            QA_ind_set2[QA_question_no[i]] = QA_set2[i].strip()
        if isinstance(QA_set3[i], str):
            QA_ind_set3[QA_question_no[i]] = QA_set3[i].strip()
        Mark_CorrectAnswer_QA[QA_question_no[i]] = C_QA_Mark_Arr[i]
        Mark_wrongAnswer_QA[QA_question_no[i]] = W_QA_Mark_Arr[i]

    return Course,GetSetCode_from_Binary,TF_ind_set1, TF_ind_set2, TF_ind_set3, QA_ind_set1, QA_ind_set2, QA_ind_set3, Mark_correctAnswer_TF, Mark_wrongAnswer_TF, Mark_CorrectAnswer_QA, Mark_wrongAnswer_QA




def stackImages(imgArray,scale):
    rows = len(imgArray)
    cols = len(imgArray[0])

    rowsAvailable = isinstance(imgArray[0], (list,np.ndarray))
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]

    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)

    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver
