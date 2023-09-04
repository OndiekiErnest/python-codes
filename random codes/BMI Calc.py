import datetime
print('Welcome to Heart Rate and \nBody Mass Index(BMI) Calculator.')
ID=str.title(input('\nWhat is your name? '))
Age=input('\nWhat is your age? (in Years) ')
Weight=input('Your weight, %s (in KILOGRAMS): '%ID)
Height=input('\nYour height (in METRES):  ')
BMI=eval('eval(Weight)/((eval(Height)**2))')
print('\n\nYour BMI is: ',BMI)
if BMI<=eval('18.5'):
    print('You are UNDERWEIGHT!\nYou need to be EATING WELL,',ID+'!')
elif BMI>=30:
    print('Sadly, you are OBESE %s!'%ID)
elif BMI>eval('24.5'):
    print('You are OVERWEIGHT, my dear',
          ID+'.\nYou are likely to be OBESE, unless you exercise!')
elif BMI>eval('18.5'):
    print('You are NORMAL,',ID+'!')
print('\nBone Mass is,',round((0.14)*((eval(Weight)))),'KG.')
print('\nYour Maximum Heart Rate is,',220-int(Age),'Beats per Minute.')
print('Your target Heart Rate is in range,',
      0.5*(220-int(Age)),'-',0.85*(220-int(Age)),'Beats per Minute.\n')
today=datetime.datetime.now()
today=today.strftime('  Executed on: %d %A of %B, %Y')
print(today)



