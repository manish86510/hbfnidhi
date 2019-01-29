from django.db import models


class UserRole(models.Model):
    role = models.CharField(max_length=100, null=True)
    comment = models.CharField(max_length=20, null=True)
    is_active = models.IntegerField(default=1)


class Customer(models.Model):
    member = models.CharField(max_length=30)
    agent = models.CharField(max_length=30, null=True)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    father_name = models.CharField(max_length=60, null=True)
    mother_name = models.CharField(max_length=60, null=True)
    husband_name = models.CharField(max_length=60, null=True)
    dob = models.CharField(max_length=30)
    gender = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    post_office = models.CharField(max_length=30, null=True)
    current_address = models.CharField(max_length=255)
    permanent_address = models.CharField(max_length=255)
    locality = models.CharField(max_length=150, null=True)
    landmark = models.CharField(max_length=80, null=True)
    pincode = models.IntegerField()
    password = models.CharField(max_length=80)
    email = models.EmailField(max_length=60)
    mobile = models.BigIntegerField()
    landline = models.CharField(max_length=15, null=True)
    is_verify = models.IntegerField()
    is_active = models.IntegerField()
    is_login = models.IntegerField()
    last_login = models.DateTimeField(auto_now_add=True)
    registration_date = models.DateTimeField(auto_now_add=True)


class UserPayment(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_mode = models.CharField(max_length=100)
    amount = models.FloatField(max_length=20)
    cash_receipt = models.CharField(max_length=20, null=True)
    cash_receipt_date = models.CharField(max_length=20, null=True)
    cheque_no = models.CharField(max_length=20, null=True)
    cheque_date = models.CharField(max_length=20, null=True)
    cheque_bank_name = models.CharField(max_length=40, null=True)
    cheque_branch_name = models.CharField(max_length=40, null=True)
    cheque_branch_ifsc = models.CharField(max_length=20, null=True)
    dd_no = models.CharField(max_length=20, null=True)
    dd_date = models.CharField(max_length=20, null=True)
    dd_bank_name = models.CharField(max_length=40, null=True)
    dd_branch_name = models.CharField(max_length=40, null=True)
    dd_branch_ifsc = models.CharField(max_length=20, null=True)


class UserFamily(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    nominee_name = models.CharField(max_length=100, null=True)
    nominee_relationship = models.CharField(max_length=20, null=True)
    nominee_dob = models.CharField(max_length=20, null=True)
    guardian_name = models.CharField(max_length=20, null=True)
    guardian_relation = models.CharField(max_length=20, null=True)
    guardian_dob = models.CharField(max_length=20, null=True)
    guardian_address = models.CharField(max_length=20, null=True)
    guardian_aadhar = models.CharField(max_length=20, null=True)
    guardian_pan = models.CharField(max_length=20, null=True)
    guardian_id = models.CharField(max_length=20, null=True)
    guardian_id_doc = models.CharField(max_length=200, null=True)
    guardian_aadhar_doc = models.CharField(max_length=200, null=True)
    guardian_pan_doc = models.CharField(max_length=200, null=True)


class UserDocument(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    aadhar = models.CharField(max_length=20, null=True)
    pan = models.CharField(max_length=20, null=True)
    id_proof = models.CharField(max_length=20, null=True)
    id_doc = models.FileField(upload_to='documents/')
    aadhar_doc = models.FileField(upload_to='documents/')
    pan_doc = models.FileField(upload_to='documents/')
    other_id = models.CharField(max_length=20, null=True)
    other_id_doc = models.FileField(upload_to='documents/')


class UserOther(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=100, null=True)
    occupation = models.CharField(max_length=20, null=True)
    income = models.CharField(max_length=20, null=True)
    income_amount = models.CharField(max_length=20, null=True)
    category = models.CharField(max_length=20, null=True)
    religion = models.CharField(max_length=20, null=True)
    occupation_type = models.CharField(max_length=20, null=True)
    vehicle = models.CharField(max_length=20, null=True)
    life_insurance = models.CharField(max_length=20, null=True)
    existing_loan = models.CharField(max_length=20, null=True)
    house = models.CharField(max_length=20, null=True)
    mutual_fund = models.CharField(max_length=200, null=True)


class Admin(models.Model):
    role = models.CharField(max_length=20, null=True)
    admin_name = models.CharField(max_length=20, null=True)
    position = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=80, null=True)
    password = models.CharField(max_length=200, null=True)
    contact = models.CharField(max_length=80, null=True)
    address = models.CharField(max_length=250, null=True)
    description = models.CharField(max_length=250, null=True)
    facebook = models.CharField(max_length=250, null=True)
    twitter = models.CharField(max_length=250, null=True)
    linkedin = models.CharField(max_length=250, null=True)
    is_active = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)


class SavingAccount(models.Model):
    member = models.CharField(max_length=20)
    account_no = models.CharField(max_length=20)
    ifsc = models.CharField(max_length=20, null=True)
    branch_code = models.CharField(max_length=80, null=True)
    branch_name = models.CharField(max_length=200, null=True)
    account_balance = models.CharField(max_length=80, null=True)
    status = models.CharField(max_length=20)
    is_active = models.IntegerField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)


class Beneficiary(models.Model):
    associated_member = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account_no = models.CharField(max_length=20, null=True)
    ifsc = models.CharField(max_length=20, null=True)
    branch_code = models.CharField(max_length=20, null=True)
    bank_name = models.CharField(max_length=40, null=True)
    contact_no = models.CharField(max_length=40, null=True)
    type_of_account = models.CharField(max_length=20, null=True)
    created_date = models.DateTimeField(auto_now_add=True)


class DebitTransaction(models.Model):
    member = models.CharField(max_length=20, unique=True)
    transaction = models.CharField(max_length=20, unique=True)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    amount = models.CharField(max_length=20, null=True)
    transaction_charge = models.CharField(max_length=20, null=True)
    transaction_amount = models.CharField(max_length=20, null=True)
    bal_before_transaction = models.CharField(max_length=20)
    bal_after_transaction = models.CharField(max_length=20)
    type_of_transaction = models.CharField(max_length=20, null=True)
    debit_type = models.CharField(max_length=20, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True)


class CreditTransaction(models.Model):
    member = models.CharField(max_length=20, unique=True)
    transaction = models.CharField(max_length=20, unique=True)
    amount = models.CharField(max_length=20, null=True)
    type_of_transaction = models.CharField(max_length=20, null=True)
    sender_account_no = models.CharField(max_length=20, null=True)
    sender_bank_name = models.CharField(max_length=20, null=True)
    models.CharField(max_length=20, null=True)
    debit_type = models.CharField(max_length=20, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True)


class FD(models.Model):
    associated_member = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20, unique=True)
    tenure = models.CharField(max_length=20)
    amount = models.CharField(max_length=20)
    rate_of_interest = models.CharField(max_length=20)
    maturity_amount = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    is_active = models.IntegerField(null=True)
    scheme = models.IntegerField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)


class RD(models.Model):
    associated_member = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20)
    tenure = models.CharField(max_length=20)
    amount = models.CharField(max_length=20)
    rate_of_interest = models.CharField(max_length=20)
    maturity_amount = models.CharField(max_length=20)
    is_active = models.IntegerField(null=True)
    scheme = models.IntegerField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)


class TDS(models.Model):
    associated_member = models.ForeignKey(Customer, on_delete=models.CASCADE)
    fd_or_rd = models.CharField(max_length=20)
    fd = models.ForeignKey(FD, on_delete=models.CASCADE, null=True)
    rd = models.ForeignKey(RD, on_delete=models.CASCADE, null=True)
    interest_amount = models.CharField(max_length=20)
    tds = models.CharField(max_length=20)
    interest_amt_after_tds = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)


class OtherCharge(models.Model):
    associated_member = models.ForeignKey(Customer, on_delete=models.CASCADE)
    charge_amount = models.CharField(max_length=20)
    remarks = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)


class SavingInterest(models.Model):
    associated_member = models.ForeignKey(Customer, on_delete=models.CASCADE)
    charge_amount = models.CharField(max_length=20)
    interest_rate = models.CharField(max_length=20)
    remarks = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)


class FD_scheme(models.Model):
    scheme = models.CharField(max_length=200)
    interest_rate = models.CharField(max_length=100)
    tenure = models.CharField(max_length=50)
    breakable = models.IntegerField()
    is_applicable = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)


class RD_scheme(models.Model):
    scheme = models.CharField(max_length=200)
    interest_rate = models.CharField(max_length=100)
    tenure = models.CharField(max_length=50)
    breakable = models.IntegerField()
    is_applicable = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
