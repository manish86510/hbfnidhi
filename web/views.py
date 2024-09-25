from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render
from masteradmin.models import *
import datetime, random

from django.core.mail import send_mail
from web.forms import *
import socket
socket.getaddrinfo('localhost', 8000)

# def contact_view(request):
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             name = form.cleaned_data['Name']
#             email = form.cleaned_data['Email']
#             message = form.cleaned_data['message']
            
#             send_mail(
#                 subject=name,
#                 message=message,
#                 from_email=email,
#                 # recipient_list=['priyalsinghal11@gmail.com']
#                 recipient_list = ['info@hbfnidhi.com']
#             )

            
           
#     else:
#         form = ContactForm()

#     return render(request, 'web/index.html', {'form': form})

#     # return render(request, 'Customer/Accounts.html', context)



def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extracting form data
            name = form.cleaned_data['Name']
            email = form.cleaned_data['Email']
            message = form.cleaned_data['message']
            
            try:
                # Sending email using send_mail function
                send_mail(
                    subject=f'Contact Form Submission from {name}',  # Subject of the email
                    message=message,  # Message body of the email
                    from_email='info@hbfnidhi.com',  # Sender email address from settings
                    recipient_list=['info@hbfnidhi.com'],  # Recipient email address
                    fail_silently=False,  # Raise error if email sending fails
                )
                success_message = "Email sent successfully."
            except Exception as e:
                success_message = f"Failed to send email: {e}"
            
            
            # Rendering the template with a success message
            return render(request, 'web/index.html', {'form': form, 'success_message': success_message})
    else:
        form = ContactForm()

    # Rendering the template with the contact form
    return render(request, 'web/index.html', {'form': form})



def index(self):
    return render(self, 'web/index.html')


def about(self):
    return render(self, 'web/about.html')


def team(self):
    return render(self, 'web/team.html')


def shareholder(self):
    return render(self, 'web/shareholder.html')


# def doorstap(self):
#     return render(self, 'web/doorstep-services.html')


def enquiry(self):
    return render(self, 'web/enquiry.html')


def saving(self):
    return render(self, 'web/saving-accounting.html')


def fixed(self):
    return render(self, 'web/fixed-deposit.html')


def recurring(self):
    return render(self, 'web/recurring-deposit.html')

def monthlyincome(self):
    return render(self, 'web/monthly-income-plan.html')

def registration(self):
    return render(self, 'web/registration.html')


def loans(self):
    return render(self, 'web/loans.html')


# def lockers(self):
#     return render(self, 'web/lockers.html')


def contact(self):
    return render(self, 'web/contact.html')

def goldloan(self):
    return render(self,'web/gold-loan.html')


def loanagainstgovtbond(self):
    return render(self, 'web/loan-against-govt-bond.html')

def loanagainstinsurancepolicy(self):
    return render(self, 'web/loan-against-insurance-policy.html')

def loanagainstdepositreceipt(self):
    return render(self, 'web/deposit-receipt.html')



def create_account(self):
    if self.method == 'POST':
        
        first_name = self.POST.get('title')+ ' ' + self.POST.get('first_name')
        date_of_birth = self.POST.get('dob')
        d = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        today = datetime.date.today()
        age = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
        
        if Customer.objects.filter(email=self.POST.get('email')).exists():
            message = "This email is already registered!"
            return render(self, 'web/registration.html', {'message': message})

        if Customer.objects.filter(mobile=self.POST.get('mobile')).exists():
            message = "This mobile number is already registered!"
            return render(self, 'web/registration.html', {'message': message})

        try:
            Customer.objects.exclude(email=self.POST.get('email'), mobile=self.POST.get('mobile'))
            
        except:
            message = "Email and Contact details already exists !"
            return render(self, 'web/registration.html', {'message': message})

        try:
            rend_num = random.randint(1111111, 9999999)
            Customer.objects.exclude(member="MA"+str(rend_num))
        except:
            rend_num = random.randint(1111111, 9999999)

        try:
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=self.POST.get('last_name'),
                member="MA"+str(rend_num),
                
                role=UserRole.objects.last(),
                father_name=self.POST.get('father_name'),
                mother_name=self.POST.get('mother_name'),
                dob=self.POST.get('dob'),
                gender=self.POST.get('gender'),
                city=self.POST.get('city'),
                state=self.POST.get('state'),
                post_office=self.POST.get('po'),
                current_address=self.POST.get('current_address'),
                permanent_address=self.POST.get('permanent_address'),
                locality=self.POST.get('locality'),
                landmark=self.POST.get('landmark'),
                pincode=self.POST.get('pincode'),
                password=self.POST.get('mobile'),
                email=self.POST.get('email'),
                mobile=self.POST.get('mobile'),
                age=age,
                landline=self.POST.get('landline'),
                is_verify=0,
                is_active=0,
                is_login=0,
                last_login=models.DateTimeField(auto_now_add=True),
                registration_date=models.DateTimeField(auto_now_add=True),
            )
            customer.save()
            message = "Form submitted successfully !"
            # return render(self, 'web/registration.html', {'message': message})
        except :
            customer = None

            
        try:
            payment = UserPayment.objects.create(
                user=Customer.objects.last(),
                payment_mode=self.POST.get('pay_mode'),
                amount=self.POST.get('amount'),
                cash_receipt=self.POST.get('cash_receipt_no'),
                cash_receipt_date=self.POST.get('cash_receipt_date'),
                cheque_no=self.POST.get('cheque_no'),
                cheque_date=self.POST.get('cheque_date'),
                cheque_bank_name=self.POST.get('cheque_bank_name'),
                cheque_branch_name=self.POST.get('cheque_branch_name'),
                cheque_branch_ifsc=self.POST.get('cheque_branch_ifsc'),
                dd_no=self.POST.get('dd_no'),
                dd_date=self.POST.get('dd_date'),
                dd_bank_name=self.POST.get('dd_bank_name'),
                dd_branch_name=self.POST.get('dd_branch_name'),
                dd_branch_ifsc=self.POST.get('dd_branch_ifsc'),
            )
         
            payment.save()
            message = "Form submitted successfully !"
        except :
            print("Error saving payment")
        try:
            family = UserFamily.objects.create(
                user=Customer.objects.last(),
                nominee_name=self.POST.get('nominee'),
                nominee_relationship=self.POST.get('nrelation'),
                nominee_dob=self.POST.get('ndob'),
                guardian_name=self.POST.get('guardian_name'),
                guardian_relation=self.POST.get('guardian_relationship'),
                guardian_dob=self.POST.get('guardian_address'),
                guardian_address=self.POST.get('cheque_bank_name'),
                guardian_aadhar=self.POST.get('guardian_aadhar'),
                guardian_pan=self.POST.get('guardian_pan'),
                guardian_id=self.POST.get('guardian_id'),
            )
            family.save()
            message = "Form submitted successfully !"
        except :
            print("Error saving  family:")
        try:
            if self.FILES['aadhar_doc']:
                aadhardoc = self.FILES['aadhar_doc']
                fs = FileSystemStorage()
                filename = fs.save(aadhardoc.name, aadhardoc)
                uploaded_file_url = fs.url(filename)
            if self.FILES['id_proof_doc']:
                iddoc = self.FILES['id_proof_doc']
                fs = FileSystemStorage()
                filename = fs.save(iddoc.name, iddoc)
                uploaded_file_url = fs.url(filename)
            if self.FILES['pan_doc']:
                pandoc = self.FILES['pan_doc']
                fs = FileSystemStorage()
                filename = fs.save(pandoc.name, pandoc)
                uploaded_file_url = fs.url(filename)
            if self.FILES['other_proof_doc']:
                otherdoc = self.FILES['other_proof_doc']
                fs = FileSystemStorage()
                filename = fs.save(otherdoc.name, otherdoc)
                uploaded_file_url = fs.url(filename)
            document = UserDocument(
                user=Customer.objects.last(),
                aadhar=self.POST.get('aadhar_no'),
                pan=self.POST.get('pan_no'),
                id_proof=self.POST.get('id_proof'),
                id_doc=iddoc.name,
                aadhar_doc=aadhardoc.name,
                pan_doc=pandoc.name,
                other_id=self.POST.get('other_proof'),
                other_id_doc=otherdoc.name,
            )
            document.save()
            other = UserOther.objects.create(
                user=Customer.objects.last(),
                qualification=self.POST.get('qualification'),
                occupation=self.POST.get('occupation'),
                income=self.POST.get('income'),
                income_amount=self.POST.get('income_amount'),
                category=self.POST.get('category'),
                religion=self.POST.get('religion'),
                vehicle=self.POST.get('vehicle'),
                life_insurance=self.POST.get('life_insurance'),
                existing_loan=self.POST.get('loans'),
                house=self.POST.get('house'),
                mutual_fund=self.POST.get('mutual_fund'),
            )
            other.save()
            message = "Form Submitted Successfully !"
        except Exception:
            other = None
        message = "Form submitted successfully !"
        return render(self, 'web/registration.html', {'message': message})
    else:
        return render(self, 'web/registration.html')



