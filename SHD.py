from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import cv2
import imutils
import pytesseract
from skimage.segmentation import clear_border
from pymongo import MongoClient
import serial
import struct

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#Method for extracting and reading Arabic numbers after segmentation
def extracting_number(image):
    extractedNumber = ""
    #Preprocessing Cropped Image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(3,3), 0)
    thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
                cv2.THRESH_BINARY_INV, 7,10)
    thresh = clear_border(thresh)
    kernel = np.ones((3,3), np.uint8)
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    #Controuring the digits
    groupCnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
    groupCnts = groupCnts[1] if imutils.is_cv3() else groupCnts[0]
    #Sorting the contours according to x
    sorted_ctrs = sorted(groupCnts, key=lambda c: cv2.boundingRect(c)[0])
    groupLocs = []
    for (i, c) in enumerate(sorted_ctrs):
    # compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)
        if w >= 8 and h >= 8 and w<= 50 and h<= 50:
            cv2.rectangle(gray, (x,y), (x+w, y+h), (255,0,0), 1)
            groupLocs.append((x, y, w, h))
            croppedImage = image[y:y+h, x:x+w]
            custom_config = r'-l ara_number --psm 13'
            extractedText = pytesseract.image_to_string(croppedImage, config=custom_config)
            extractedNumber += (extractedText.replace('\n\x0c',''))
    return dilate, gray, extractedNumber


#Method for counting amount of money needed from the database 
def countBankNotes(money,moneyDB):
	notes = [200,100,50,20,10]
	returnedNoteCounter1 = [0,0,0,0,0]
	returnedNoteCounter2 = [0,0,0,0,0]
	money1 = money
	money2 = money
	moneyDB1 = [0,0,0,0,0]
	moneyDB2 = [0,0,0,0,0]
	totalSum = 0
	extraMoney = 0
	for i in range(5):
		moneyDB1[i] = moneyDB[i]
		moneyDB2[i] = moneyDB[i]
	for i in range(5):
		if money1 >= notes[i]:
			trialCounter = money1 / notes[i]
			if(moneyDB1[i] >= int(trialCounter)) :
				money1 = money1 - int(trialCounter) * notes[i]
				moneyDB1[i] = moneyDB1[i] - int(trialCounter)
				returnedNoteCounter1[i] = int(trialCounter)
			elif(moneyDB1[i] > 0 and (int(trialCounter) > moneyDB1[i])):
				trialCounter = moneyDB1[i]
				money1 = money1 - trialCounter * notes[i]
				moneyDB1[i] = moneyDB1[i] - trialCounter
				returnedNoteCounter1[i] = trialCounter
			else:
				returnedNoteCounter1[i] = 0
		else:
			returnedNoteCounter1[i] = 0
	if(money1 == 0):
		return returnedNoteCounter1[0], returnedNoteCounter1[1], returnedNoteCounter1[2], returnedNoteCounter1[3], returnedNoteCounter1[4]
	else:
		for i in range(5):
			totalSum += notes[i] * moneyDB2[i]
		if(totalSum == money2):
			for i in range(5):
				returnedNoteCounter2[i] = moneyDB2[i]
				moneyDB2[i] = 0
		elif(totalSum > money2):
			extraMoney = totalSum - money2
			for i in range(5):
				trialCounter = extraMoney / notes[i]
				if(moneyDB2[i] >= int(trialCounter)):
					returnedNoteCounter2[i] = moneyDB2[i] - int(trialCounter)
					moneyDB2[i] = int(trialCounter)
					extraMoney = extraMoney - int(moneyDB2[i]) * notes[i]
				else:
					extraMoney = extraMoney - int(moneyDB2[i]) * notes[i]
					returnedNoteCounter2[i] = 0
		if(returnedNoteCounter2[0] == 0 and returnedNoteCounter2[1] == 0 and returnedNoteCounter2[2] == 0 and returnedNoteCounter2[3] == 0 and returnedNoteCounter2[4] == 0):
			print("You need "+str(money)+"LE and the cash dispenser only has "+str(totalSum)+"LE")
			print("----------------------")
		else:
			if(extraMoney != 0):
				print("You have an extra "+str(extraMoney)+"LE")
		return returnedNoteCounter2[0], returnedNoteCounter2[1], returnedNoteCounter2[2], returnedNoteCounter2[3], returnedNoteCounter2[4]


#Connecting to Arduino
#ser = serial.Serial('COM5', 9600)

#Connecting to database and getting info from the last records
client = MongoClient("mongodb+srv://youssrabouyoussif:Ya.12345@cluster0-ga4kc.mongodb.net/test?retryWrites=true&w=majority")
lastRecord = client.SHD.billsInfo.find_one(
  sort=[( '_id', -1 )]
)
bankNoteRecord = client.SHD.bankNotes.find_one(
  sort=[( '_id', -1 )]
)
j = 0
allRecords = []
for i in client.SHD.billsInfo.find():
	allRecords.append(i)
	j = j + 1

if len(allRecords) > 0:
	j = 0
	allBillNumbers = []
	for i in range(len(allRecords)):
		billBybill = allRecords[i]
		allBillNumbers.append(billBybill['billNumber'])

j = 0
allRecordsUnpaid = []
for i in client.SHD.unpaidBills.find():
	allRecordsUnpaid.append(i)
	j = j + 1

if len(allRecordsUnpaid) > 0:
	j = 0
	allBillNumbersUnpaid = []
	for i in range(len(allRecordsUnpaid)):
		billByBillUnpaid = allRecordsUnpaid[i]
		allBillNumbersUnpaid.append(billByBillUnpaid['billNumber'])

print("Connected to MongoDB")
print("----------------------")

##load the image and compute the ratio of the old height
##to the new height, clone it, and resize it
image = cv2.imread("4_10.jpeg")
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height = 500)

##convert the image to grayscale, blur it, and find edges
##in the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)
##find the contours in the edged image, keeping only the
##largest ones, and initialize the screen contour
cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

##loop over the contours
for c in cnts:
	##approximate the contour
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	##if our approximated contour has four points, then we
	##can assume that we have found our screen
	if len(approx) == 4:
		screenCnt = approx
		break

##apply the four point transform to obtain a top-down
##view of the original image
warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
cropped = cv2.resize(warped, (640,927))

#Extracting and reading Arabic text
participantText = cropped[200:250,460:621]
custom_config = r'-l ara --psm 6'
participantText = pytesseract.image_to_string(participantText, config=custom_config)

billNumberText = cropped[410:460,410:602]
custom_config = r'-l ara --psm 6'
billNumberText = pytesseract.image_to_string(billNumberText, config=custom_config)

dateText = cropped[470:545,410:600]
custom_config = r'-l ara --psm 9'
dateText = pytesseract.image_to_string(dateText, config=custom_config)

numberOfMonthsText = cropped[540:605,410:600]
custom_config = r'-l ara --psm 10'
numberOfMonthsText = pytesseract.image_to_string(numberOfMonthsText, config=custom_config)

moneyText = cropped[755:810,405:597]
custom_config = r'-l ara --psm 13'
moneyText = pytesseract.image_to_string(moneyText, config=custom_config)

#Cropping Arabic numbers images and extracting information using previous defined method
participantNumberImage = cropped[200:270,70:440]
dilateParticipant, grayParticipant, participantNumber = extracting_number(participantNumberImage)
print("Image is cropped successfully!")
print("----------------------")

if (lastRecord and bankNoteRecord):
	participantNumberDB = lastRecord['participantNumber']
	billNumberDB = lastRecord['billNumber']
	dateDB = lastRecord['date']
	yearDB = dateDB[0:4]
	monthDB = dateDB[5:]
	numberOfMonthsDB = lastRecord['numberOfMonths']
	moneyDB = lastRecord['money']

	money200DB = bankNoteRecord['money200']
	money100DB = bankNoteRecord['money100']
	money50DB = bankNoteRecord['money50']
	money20DB = bankNoteRecord['money20']
	money10DB = bankNoteRecord['money10']

	if participantNumber != participantNumberDB:
		print("Sorry! The participant number extracted is "+participantNumber+", while the correct participant number is "+participantNumberDB)
		print("----------------------")
		#ser.write(struct.pack('>BBBBB',200,200,200,200,200))
	else :
		print("Valid Participant Number!")
		print("----------------------")
		billNumberImage = cropped[410:480,100:400]
		dilateBillNumber, grayBillNumber, billNumber = extracting_number(billNumberImage)
		billNumberRepeated = False
		for i in range(len(allBillNumbers)):
			if billNumber == allBillNumbers[i]:
				billNumberRepeated = True
				break
		if billNumberRepeated == True:
			print("Sorry! A bill with the same Bill Number has been paid before!")
			print("----------------------")
			#ser.write(struct.pack('>BBBBB',210,210,210,210,210))
		else:
			print("Valid Bill Number!")
			print("----------------------")
			dateNumberImage = cropped[470:545,100:400]
			dilateDate, grayDate, dateNumber = extracting_number(dateNumberImage)
			numberOfMonthsImage = cropped[540:615,100:400]
			dilatenumberOfMonths, grayNumberOfMonths, numberOfMonths = extracting_number(numberOfMonthsImage)
			year = dateNumber[0:4]
			month = dateNumber[4:]
			intYear = int(year)
			intYearDB = int(yearDB)
			intMonth = int(month)
			intMonthDB = int(monthDB)
			intNumberOfMonthsDB = int(numberOfMonthsDB)
			intNumberOfMonths = int(numberOfMonths)
			if intYear < intYearDB or (intMonth <= intMonthDB and intYear <= intYearDB) or ((intMonth - intNumberOfMonths + 1) <= intMonthDB and intYear <= intYearDB):
				if intNumberOfMonths > 1:
					intMonthsPaid = intMonth - intNumberOfMonths +1
					print("Sorry! The extracted bill is for year "+str(intYear)+" for months "+str(intMonth)+" and "+str(intMonthsPaid)+
					" while the last paid bill was paid in "+str(intMonthDB)+"/"+str(intYearDB))
					print("----------------------")
				else:
					print("Sorry! The date extracted is " +str(intMonth)+"/"+str(intYear)+" and the last paid bill was in "+str(intMonthDB)+"/"+str(intYearDB))
					print("----------------------")
				#ser.write(struct.pack('>BBBBB',220,220,220,220,220))
			else:
				print("Valid Date!")
				print("----------------------")
				moneyNumberImage = cropped[750:830,100:400]
				dilateMoney, grayMoney, moneyNumber = extracting_number(moneyNumberImage)
				moneyDBCheck = [money200DB,money100DB,money50DB,money20DB,money10DB]
				neededMoney200, neededMoney100, neededMoney50, neededMoney20, neededMoney10 = countBankNotes(int(moneyNumber),moneyDBCheck)
				if(neededMoney200 != 0 or neededMoney100 != 0 or neededMoney50 != 0 or neededMoney20 != 0 or neededMoney10 != 0) :
					print(str(neededMoney200)+" banknote/s is/are needed from the 200s\n"+str(neededMoney100)+" banknote/s is/are needed from the 100s\n"
					+str(neededMoney50)+" banknote/s is/are needed from the 50s\n"+str(neededMoney20)+" banknote/s is/are needed from the 20s\n"
					+str(neededMoney10)+" banknote/s is/are needed from the 10s")
					print("----------------------")
					print("Cash dispenser has enough money!")
					print("----------------------")
					collection = {
							'participantNumber':participantNumber,
							'billNumber':billNumber,
							'date':year+" "+month,
							'numberOfMonths':numberOfMonths,
							'money':moneyNumber
						}
					myquery = { 
							"money200": money200DB,
							"money100": money100DB,
							"money50": money50DB,
							"money20": money20DB,
							"money10": money10DB 
						}
					money200DB = money200DB - neededMoney200
					money100DB = money100DB - neededMoney100
					money50DB = money50DB - neededMoney50
					money20DB = money20DB - neededMoney20
					money10DB = money10DB - neededMoney10
					newvalues = { "$set": { "money200": money200DB,
							"money100": money100DB,
							"money50": money50DB,
							"money20": money20DB,
							"money10": money10DB } 
						}
					client.SHD.billsInfo.insert_one(collection)
					client.SHD.bankNotes.update_one(myquery, newvalues)
					print("Sending to Arduino")
					print("----------------------")
					#ser.write(struct.pack('>BBBBB',neededMoney200,neededMoney100,neededMoney50,neededMoney20,neededMoney10))
					print("Money has been paid successfully and record is inserted in the database!")
					print("----------------------")
				else:
					for i in range(len(allBillNumbersUnpaid)):
						if billNumber == allBillNumbersUnpaid[i]:
							billNumberRepeated = True
							break
					if billNumberRepeated == False:
						collection = {
							'participantNumber':participantNumber,
							'billNumber':billNumber,
							'date':year+" "+month,
							'numberOfMonths':numberOfMonths,
							'money':moneyNumber
						}
						client.SHD.unpaidBills.insert_one(collection)
					print("Sorry the cash dispenser does not have enough money!")
					print("----------------------")
					#ser.write(struct.pack('>BBBBB',230,230,230,230,230))

else :
	billNumberImage = cropped[410:480,100:400]
	dilateBillNumber, grayBillNumber, billNumber = extracting_number(billNumberImage)
	dateNumberImage = cropped[470:545,100:400]
	dilateDate, grayDate, dateNumber = extracting_number(dateNumberImage)
	numberOfMonthsImage = cropped[540:615,100:400]
	dilatenumberOfMonths, grayNumberOfMonths, numberOfMonths = extracting_number(numberOfMonthsImage)
	year = dateNumber[0:4]
	month = dateNumber[4:]
	moneyNumberImage = cropped[750:830,100:400]
	dilateMoney, grayMoney, moneyNumber = extracting_number(moneyNumberImage)
	moneyDBCheck = [money200DB,money100DB,money50DB,money20DB,money10DB]
	notesCounter = countBankNotes(int(moneyNumber),moneyDBCheck)
	if(neededMoney200 != 0 or neededMoney100 != 0 or neededMoney50 != 0 or neededMoney20 != 0 or neededMoney10 != 0) :
		print("Cash dispenser has enough money!")
		print("----------------------")
		collection = {
				'participantNumber':participantNumber,
				'billNumber':billNumber,
				'date':year+" "+month,
				'numberOfMonths':numberOfMonths,
				'money':moneyNumber
			}
		myquery = { 
				"money200": money200DB,
				"money100": money100DB,
				"money50": money50DB,
				"money20": money20DB,
				"money10": money10DB 
			}
		money200DB = money200DB - neededMoney200
		money100DB = money100DB - neededMoney100
		money50DB = money50DB - neededMoney50
		money20DB = money20DB - neededMoney20
		money10DB = money10DB - neededMoney10
		newvalues = { "$set": { "money200": money200DB,
				"money100": money100DB,
				"money50": money50DB,
				"money20": money20DB,
				"money10": money10DB } 
			}
		client.SHD.billsInfo.insert_one(collection)
		client.SHD.bankNotes.update_one(myquery, newvalues)
		print("Sending to Arduino")
		print("----------------------")
		#ser.write(struct.pack('>BBBBB',neededMoney200,neededMoney100,neededMoney50,neededMoney20,neededMoney10))
		print("Money has been paid successfully and record is inserted in the database!")
		print("----------------------")
	else:
		for i in range(len(allBillNumbersUnpaid)):
			if billNumber == allBillNumbersUnpaid[i]:
				billNumberRepeated = True
				break
		if billNumberRepeated == False:
			collection = {
				'participantNumber':participantNumber,
				'billNumber':billNumber,
				'date':year+" "+month,
				'numberOfMonths':numberOfMonths,
				'money':moneyNumber
			}
			client.SHD.unpaidBills.insert_one(collection)
		print("Sorry the cash dispenser does not have enough money!")
		print("----------------------")

cv2.waitKey(0)
cv2.destroyAllWindows()