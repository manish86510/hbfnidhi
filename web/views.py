from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from masteradmin.models import *
import datetime, random


def index(self):
    return render(self, 'web/index.html')


def about(self):
    return render(self, 'web/about.html')


def team(self):
    return render(self, 'web/team.html')


def shareholder(self):
    return render(self, 'web/shareholder.html')


def enquiry(self):
    return render(self, 'web/enquiry.html')


def saving(self):
    return render(self, 'web/saving.html')


def fixed(self):
    return render(self, 'web/fixedDeposite.html')


def recurring(self):
    return render(self, 'web/recurringDeposite.html')


def registration(self):
    return render(self, 'web/registration.html')


def loans(self):
    return render(self, 'web/loan.html')


def lockers(self):
    return render(self, 'web/lockers.html')


def contact(self):
    return render(self, 'web/contact.html')


def create_account(self):
    if self.method == 'POST':
        rend_num = random.randint(1111, 9999)
        first_name = self.POST.get('title')+ ' ' + self.POST.get('first_name')
        try:
            customer = Customer(
                first_name=first_name,
                last_name=self.POST.get('last_name'),
                member="MA"+str(rend_num),
                agent=self.POST.get('agent_id'),
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
                password="123456",
                email=self.POST.get('email'),
                mobile=self.POST.get('mobile'),
                landline=self.POST.get('landline'),
                is_verify=0,
                is_active=0,
                is_login=0,
                last_login=models.DateTimeField(auto_now_add=True),
                registration_date=models.DateTimeField(auto_now_add=True),
            )
            customer.save()
            payment = UserPayment(
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
            family = UserFamily(
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
            other = UserOther(
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
            message = "Something went wrong !"
    else:
        message = "Something went wrong !"
    return render(self, 'web/registration.html',{'message': message})

