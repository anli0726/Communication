from datetime import datetime
import time

class TimeStamp:
	
	def __init__(self, name):
		self.name = name

	def date(self, target="date"):
		curr = datetime.now()
		if type(target) == str:
			if target == "year":
				return curr.year
			if target == "month":
				return curr.month
			if target == "day":
				return curr.day
			if target == "date":
				month = (str(curr.month)).rjust(2,"0")
				day = (str(curr.day)).rjust(2,"0")
				year = curr.year
				return f"{month}/{day}/{year}"
		else:
			report = []
			for t in target:
				if t == "year":
					report.append(curr.year)
				if t == "month":
					report.append(curr.month)
				if t == "day":
					report.append(curr.day)
			return report

	def time(self, target="time"):
		curr = datetime.now()
		if type(target) == str:
			if target == "hour":
				return curr.hour
			if target == "minute":
				return curr.minute
			if target == "second":
				return curr.second
			if target == "msec":
				return round(curr.microsecond/1000)
			if target == "time":
				hour = (str(curr.hour)).rjust(2,"0")
				minute = (str(curr.minute)).rjust(2,"0")
				second = (str(curr.second)).rjust(2,"0")
				msec = (str(round(curr.microsecond/1000))).rjust(3,"0")
				return f"{hour}:{minute}:{second}.{msec}"
		else:
			report = []
			for t in target:
				if t == "hour":
					report.append(curr.hour)
				if t == "minute":
					report.append(curr.minute)
				if t == "second":
					report.append(curr.second)
				if t == "msec":
					report.append(round(curr.microsecond/1000))
			return report

	def datetime(self):
		date = self.date("date")
		time = self.time("time")
		return f"{date} {time}"

if __name__ == "__main__":
	timeStamp = TimeStamp("test")
	print(timeStamp.name)
	print(timeStamp.datetime())
	print(timeStamp.time("second"))
	print(timeStamp.time(["second", "msec"]))
	print(time.strftime("%m/%d/%Y %H:%M:%S", time.localtime()))
	time.sleep(2)
	print(timeStamp.datetime())
	print(timeStamp.time("second"))
	print(timeStamp.time(["second", "msec"]))
	print(time.strftime("%m/%d/%Y %H:%M:%S", time.localtime()))
