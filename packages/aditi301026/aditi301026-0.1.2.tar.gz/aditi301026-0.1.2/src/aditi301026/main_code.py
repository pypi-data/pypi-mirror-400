creator="Aditi Jain"
institue="Robotronix"
university="DAVV"
dob="30/10/2006"

def attendance_tracker():
    a=int(input("Enter the minimum percentage attendance criteria of your institude:"))
    days_attended=int(input("Enter the number of days you attended classes:"))
    held_days=int(input("Enter the number of days classes held till now:"))
    remain_days=int(input("Enter the number of days classes remaining:"))
    total_days=held_days+remain_days
    per=(days_attended/total_days)*100
    if per==a:
        print("Your attendance is completed")
        print("But recommended to attend 1 or 2 classes")
    elif per>a:
        print(f"Your attendance is completed and your attendance percentage is {per}")
    elif per<a:
        low=a-per
        print(f"Your attendance is low by {low} percentage")
        num=total_days*(low/100)
        if num<remain_days:
            print(f"you should attend {num} more classes")
        elif num==remain_days:
            print("You should attend each and every class")
        else:
            print("You're not allowed to give exams")


def result(*a):
    lam1= lambda x,y:x+y
    from functools import reduce
    num1=reduce(lam1,a)
    num2=len(a)*100
    per=(num1/num2)*100
    return f"your percentage is {per}"

def table(a):
    x = a
    stop = a*10
    while a<=stop:
        print(a)
        a=a+x

def vote_checker(age):
    if age > 18:
        print(" Congrats You can vote")
    elif age == 18:
        print(" Please apply for voter id card")
    else:
        print('You are not eligible for vote')

def calculator(operation):
    from functools import reduce

    if operation == "add":
        return lambda *a: reduce(lambda x, y: x + y, a)
    
    elif operation == "sub":
        return lambda *a: reduce(lambda x, y: x - y, a)
    
    elif operation == "mul":
        return lambda *a: reduce(lambda x, y: x * y, a)
    
    elif operation == "div":
        return lambda x, y: x / y if y != 0 else "Cannot divide by zero"
    
    elif operation == "mod":
        return lambda x, y: x % y
    
    else:
        return lambda *a: "Invalid Operation"
