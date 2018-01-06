# -*- coding: utf-8 -*-
import re
from odoo.exceptions import Warning, ValidationError
from openerp import models, fields, api
from datetime import datetime, timedelta , date
import time
from dateutil.relativedelta import relativedelta


class RegForm(models.Model):
	_name = 'reg.form'
	_rec_name = 'rec_new_name'
	_inherit = ['mail.thread']
	_description = 'Registration'


	package = fields.Many2one('reg.package', string="Package")
	service = fields.Many2many('struct.service', string="Service")
	branch = fields.Many2one('branch', string="Branch",readonly=True)
	status = fields.Many2one('reg.status', string="Status")
	current_trainer = fields.Many2one('hr.employee', string="Current Trainer")
	joining = fields.Date(string="Joining")
	last_date = fields.Date(string="Last Date")
	member_photo = fields.Binary('Member Photo')
	rejoining = fields.Date(string="Re Joining/Change Package")
	expire_date = fields.Date(string="Expiry Date")
	package_charge = fields.Float(string="Package Charges",readonly=True)
	avg_per_month = fields.Float(string="Average Per Month",readonly=True)
	ref_no = fields.Char(string="Ref No.")
	rec_new_name = fields.Char(string="rec")
	assesment = fields.Char(string="Assessment")
	total = fields.Float(string="Total",readonly=True)
	discount_type = fields.Selection([('per', 'Percentage'), ('amt', 'Amount')], string="Discount Type")
	gender = fields.Selection([('male', 'Male'), ('female', 'Female'),('other', 'Other')], string="Gender")
	trainer = fields.Selection([('self', 'Self'), ('trainer', 'Trainer')], string="Trainer")
	discount = fields.Integer(string="Discount")
	discount_amt = fields.Float(string="Discounted Amount",readonly=True)
	advance = fields.Char(string="Advance")
	balance = fields.Char(string="Balance")
	name = fields.Char(string="Full Name", required=True)
	dob = fields.Date(string="Date Of Birth")
	cnic = fields.Char(string="CNIC#")
	profession = fields.Char(string="Profession")
	organization = fields.Char(string="Organization")
	job_title = fields.Char(string="Job Title")
	home_addres = fields.Char(string="Home Address")
	office_addres = fields.Char(string="Office Address")
	tel_office = fields.Char(string="Tel")
	tel_home = fields.Char(string="Tel")
	mob = fields.Char(string="Mobile")
	email = fields.Char(string="Email")
	ntn = fields.Char(string="NTN")
	sms = fields.Boolean(string="SMS")
	morning = fields.Boolean(string="Morning")
	noon = fields.Boolean(string="Noon")
	train = fields.Boolean(string="Trainer")
	afternoon = fields.Boolean(string="Afternoon")
	evening = fields.Boolean(string="Evening")
	bol_email = fields.Boolean(string="Email")
	show_mem = fields.Boolean(string="Show",compute="compute_show_fields")
	result = fields.Boolean(string="result",compute="compute_result")
	new_join = fields.Boolean(string="new",compute="compute_new_join")
	curent_date = fields.Date(string="current",default=date.today())
	# req_date = fields.Boolean(string="required",compute="compute_required")
	ref_name = fields.Char(string="Name")
	ref_contact = fields.Char(string="Contact")
	ref_addres = fields.Char(string="Address")
	ref_realtion = fields.Char(string="Relationship")
	ref_name_1 = fields.Char(string="Name")
	ref_contact_1 = fields.Char(string="Contact")
	ref_addres_1 = fields.Char(string="Address")
	ref_realtion_1 = fields.Char(string="Relationship")
	bmi = fields.Char(string="I.BMI")
	weight = fields.Char(string="II.WEIGHT")
	fat = fields.Char(string="III.FAT%")
	emg_name = fields.Char(string="Name")
	emg_contact = fields.Char(string="Contact")
	emg_addres = fields.Char(string="Address")
	emg_name_1 = fields.Char(string="Name")
	emg_contact_1 = fields.Char(string="Contact")
	emg_addres_1 = fields.Char(string="Address")
	stages = fields.Selection([
		('leads', 'Leads'),
		('app_form', 'Registration Form'),
		('member', 'Member'),
		('non_member', 'Non Active Members'),
		('cancel', 'Cancelled'),
	], default='leads',track_visibility='onchange')

	m_time = fields.Selection([
		('79', '7 AM - 9 AM'),
		('911', '9 AM - 11 AM'),
	], string="Morning Times")

	n_time = fields.Selection([
		('111', '11 AM - 1 PM'),
		('13', '1 PM - 3 PM'),
	], string="Noon Times")

	a_time = fields.Selection([
		('35', '3 PM - 5 PM'),
	], string="Afternoon Times")

	e_time = fields.Selection([
		('57', '5 PM - 7 PM'),
		('79', '7 PM - 9 PM'),
		('910', '9 PM - 10 PM'),
	], string="Evening Times")

	memship_no = fields.Char(string="Membership No")
	seq_id = fields.Char(string="Id",readonly=True)
	member_link = fields.Many2one('res.partner', string="Member Link")
	invoice_link = fields.Many2one('account.invoice',readonly=True)
	time_slot_m = fields.Many2one('struct.slots',string="Time Slot")
	time_slot_n = fields.Many2one('struct.slots',string="Time Slot")
	time_slot_af = fields.Many2one('struct.slots',string="Time Slot")
	time_slot_e = fields.Many2one('struct.slots',string="Time Slot")
	payment_terms = fields.Many2one('account.payment.term', string="Payment Terms")
	due_amt = fields.Float(string="Due Amount",compute="compute_due_amt")

	_sql_constraints = [
	('memship_no', 'unique(memship_no)','This Membership Number Already Esixts!')
	]


	@api.multi
	def monthly_invoice(self):
		today_date=time.strftime("%Y-%m-%d")
		records = self.env['reg.form'].search([('last_date','<=',today_date),('stages','=','member')])
		sale_rec = self.env['struct.sale'].search([])
		for x in records:
			invoice_already=self.env['account.invoice'].search([('date_invoice','=',x.last_date),('partner_id','=',x.member_link.id)])
			if not invoice_already:
				if re.findall('([0-9]+)', x.payment_terms.name):
					n = int(re.findall('([0-9]+)', x.payment_terms.name)[0])
				else:
					n = 0
				invoice_entries = self.env['account.invoice'].search([])
				create_invoice_entry = invoice_entries.create({
					'partner_id': x.member_link.id,
					'membership_no': x.memship_no,
					'branch': x.branch.id,
					'payment_term_id': x.payment_terms.id,
					'due_date': datetime.now() + timedelta(days=n),
					'date_invoice': x.last_date,
					'type': 'out_invoice',
				})

				for z in x.service:
					for y in x.package.pakg_tree:
						if z.name == y.service.name:
							a = create_invoice_entry.invoice_line_ids.create({
								'price_unit': y.amount,
								'account_id': y.pakg_id.accounts.id,
								'name': y.service.name,
								'invoice_id': create_invoice_entry.id,
							})
				x.last_date = datetime.now() + relativedelta(months=x.package.month)

		for z in sale_rec:
			if x.stages == "draft":
				x.stages = 'invoice'
				invoice_entries = self.env['account.invoice'].search([])
				create_invoice_entry = invoice_entries.create({
						'partner_id': x.name.id,
						'branch': x.branch.id,
						'date_invoice': x.date,
						'membership_no':x.membership_no.memship_no,
						'type': 'out_invoice',

					})

				for y in x.sale_id:
					a = create_invoice_entry.invoice_line_ids.create({
						'price_unit': y.subtotal,
						'account_id': 27,
						'name': y.product.name,
						'invoice_id': create_invoice_entry.id,
					})

				x.invoice_link = create_invoice_entry.id


	@api.multi
	def write(self, vals):
		super(RegForm, self).write(vals)
		if self.stages == 'app_form':
			if self.package:
				if self.morning == False and self.noon == False and self.evening == False and self.afternoon == False:
					raise  ValidationError('Select Timeslot')

		return True

	@api.one
	def compute_due_amt(self):
		if self.invoice_link:
			self.due_amt = self.invoice_link.due_amt


	@api.one
	def compute_result(self):
		if self.invoice_link:
			if self.stages == 'app_form' and self.show_mem == True:
				self.result = True



	# @api.one
	# def compute_required(self):
	# 	if self.result == True and 


	@api.one
	def compute_new_join(self):
		if self.result == False and self.stages == 'app_form':
			self.new_join = True


	@api.one
	def compute_show_fields(self):
		if self.invoice_link:
			if self.invoice_link.stages != 'draft':
				if self.invoice_link.due_amt != self.invoice_link.amount_total:
					self.show_mem = True


	@api.model
	def create(self, vals):
		vals['seq_id'] = self.env['ir.sequence'].next_by_code('mem.seq')
		new_record = super(RegForm, self).create(vals)

		return new_record

	def create_member(self):
		self.stages = 'member'
		self.member_link = self.invoice_link.partner_id.id

	def cancel(self):
		self.stages = 'cancel'
		if self.invoice_link:
			self.invoice_link.unlink()
		# member_entries = self.env['res.partner'].search([('id', '=', self.member_link.id)])
		# if not member_entries:
		# 	create_member_entry = member_entries.create({
		# 		'name': self.name,
		# 	})
		# 	self.member_link = create_member_entry.id

	@api.multi
	def unlink(self):
		for x in self:
			if x.stages == "member" or x.stages == "non_member" or x.stages == "app_form":
				raise  ValidationError('Cannot Delete Record')
	
		return super(RegForm,self).unlink()

	@api.multi
	def app_form(self):
		self.stages = 'app_form'

	@api.multi
	def non_member(self):
		return {'name': 'Confirmation',
				'domain': [],
				'res_model': 'confirm',
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'view_type': 'form',
				'context': {'default_reg_link':self.id},
				'target': 'new', }

	@api.onchange('name')
	def get_branch(self):
		users = self.env['res.users'].search([('id','=',self._uid)])
		if self.name:
			self.branch = users.branch.id




	# @api.one
	# @api.constrains('memship_no')
	# def get_unique_no(self):
	# 	if self.memship_no:
	# 		rec = self.env['reg.form'].search([('memship_no','=',self.memship_no.id),('id','!=',self.id)])
	# 		if rec:
	# 			raise ValidationError('This Membership No Already Allotted')




	@api.multi
	def create_invoice(self):
		
		member_entries = self.env['res.partner'].search([])
		create_member = member_entries.create({
				'name': self.name,
			})
		if re.findall('([0-9]+)', self.payment_terms.name):
			x = int(re.findall('([0-9]+)', self.payment_terms.name)[0])
		else:
			x = 0

		if self.invoice_link:
			self.invoice_link.unlink()
			
	
		if self.stages == 'app_form':
			value = 0
			discount = " "
			invoice_entries = self.env['account.invoice'].search([])
			create_invoice_entry = invoice_entries.create({
				'partner_id': create_member.id,
				'branch': self.branch.id,
				'payment_term_id': self.payment_terms.id,
				'due_date': datetime.now() + timedelta(days=x),
				'date_invoice': datetime.now(),
				'member': True,
				'type': 'out_invoice',
			})

			b = create_invoice_entry.invoice_line_ids.create({
				'price_unit': self.package.reg_fee,
				'account_id': self.package.accounts.id,
				'name': 'Membership Fee',
				'invoice_id': create_invoice_entry.id,
			})

			for x in self.service:
				for y in self.package.pakg_tree:
					if x.name == y.service.name:
						a = create_invoice_entry.invoice_line_ids.create({
							'price_unit': y.amount,
							'account_id': y.pakg_id.accounts.id,
							'name': y.service.name,
							'invoice_id': create_invoice_entry.id,
						})

			if self.discount > 0:

				if self.discount_type == 'amt' and self.discount:
					value = (self.discount) * -1.0
					discount = str(self.discount) + 'Rs' 
				if self.discount_type == 'per' and self.discount:
					value = (self.total - self.discount_amt) * -1.0
					discount = str(self.discount) + '%'

				c = create_invoice_entry.invoice_line_ids.create({
					'price_unit': value,
					'account_id': self.package.accounts.id,
					'name': 'Discount' + ' ' + str(discount),
					'invoice_id': create_invoice_entry.id,
				})

			self.invoice_link = create_invoice_entry.id
			self.last_date = datetime.now() + relativedelta(months=self.package.month)




				# if self.discount_type == 'per' and self.discount:
				# 	d = create_invoice_entry.invoice_line_ids.create({
				# 		'price_unit': (self.total - self.discount_amt) * -1.0,
				# 		'account_id': 27,
				# 		'name': str(self.discount) + ' Discount',
				# 		'invoice_id': create_invoice_entry.id,
				# 	})

			

	@api.onchange('morning')
	def select_one(self):
		if self.morning == True:
			self.noon = False
			self.afternoon = False
			self.evening = False
			self.time_slot_m = False

	@api.onchange('noon')
	def select_one1(self):
		if self.noon == True:
			self.morning = False
			self.afternoon = False
			self.evening = False
			self.time_slot_n = False

	@api.onchange('afternoon')
	def select_one2(self):
		if self.afternoon == True:
			self.morning = False
			self.noon = False
			self.evening = False
			self.time_slot_af = False

	@api.onchange('evening')
	def select_one3(self):
		if self.evening == True:
			self.morning = False
			self.noon = False
			self.afternoon = False
			self.time_slot_e = False

	@api.onchange('package', 'service')
	def get_total(self):
		if self.package:
			value = 0
			self.total = self.package.reg_fee
			for x in self.service:
				for y in self.package.pakg_tree:
					if x.name == y.service.name:
						value = value + y.amount
						self.package_charge = value
						self.total = self.total + y.amount


	@api.onchange('package_charge')
	def get_per_month(self):
		if self.package_charge:
			self.avg_per_month = self.package_charge / self.package.month

	@api.onchange('name','memship_no')
	def get_rec_nam(self):
		self.rec_new_name = str(self.name) + ' ' + str(self.memship_no)


	# @api.onchange('joining')
	# def get_invoice_day(self):
	# 	if self.joining:
	# 		self.invoiced_date = datetime.strptime(self.joining,'%Y-%m-%d').strftime('%d')
			


	@api.onchange('discount', 'total', 'discount_type')
	def get_discount(self):
		if self.discount_type and self.total > 0:
			if self.discount_type == 'amt':
				self.discount_amt = self.total - self.discount
			if self.discount_type == 'per':
				if self.discount <= 100:
					value = self.total * (self.discount / 100.0)
					self.discount_amt = self.total - value
				else:
					raise ValidationError('Discount Can not be more than 100%')

	# if self.discount_type == False:
	# 	print "1111111111111111111111111"
	# 	self.discount_amt = self.total
	# 	self.discount = 0

	# @api.onchange('joining')
	# def get_expiry(self):
	# 	if self.package:
	# 		self.expire_date = \
	# 			(datetime.strptime(self.joining, '%Y-%m-%d') + relativedelta(months=self.package.month)).strftime(
	# 				'%Y-%m-%d')


# class RegBranch(models.Model):
#     _name = 'reg.branch'

#     name = fields.Char(string='Name')


class RegStatus(models.Model):
	_name = 'reg.status'

	name = fields.Char(string='Name')


class RegAccount(models.Model):
	_inherit = 'account.invoice'

	branch = fields.Many2one('branch', string='Branch',readonly=True)
	due_date = fields.Date(string='Due Date',readonly=True)
	status = fields.Many2one('reg.status',string='Status')
	check = fields.Boolean()
	member = fields.Boolean()
	rejoin = fields.Boolean()
	membership_no = fields.Char(string='Membership No.',readonly=True)
	customer_name = fields.Char(string="Customer Name")
	discount_amt = fields.Float(string="Discounted Amount")
	due_amt = fields.Float(string="Amount Due",readonly=True)
	customer_payment_id_1 = fields.One2many('customer.payment.bcube', 'invoice_link',readonly=True)
	stages = fields.Selection([
			('draft','Draft'),
			('proforma', 'Pro-forma'),
			('proforma2', 'Pro-forma'),
			('open', 'Open'),
			('paid', 'Paid'),
			('new', 'Paid'),
			('cancel', 'Cancelled'),
		], string='Status', index=True, readonly=True, default='draft',
		track_visibility='onchange', copy=False)


	@api.multi
	def action_invoice_open(self):
		new_record = super(RegAccount, self).action_invoice_open()
		self.due_amt = self.amount_total
		self.stages = 'open'

   
		return new_record



	@api.multi
	def reg_pay(self):
		return {'name': 'Receipt',
				'domain': [],
				'res_model': 'customer.payment.bcube',
				'type': 'ir.actions.act_window',
				'view_mode': 'form', 'view_type': 'form',
				'context': {'default_branch':self.branch.id,
				'default_partner_id':self.partner_id.id,
				'default_membership_no':self.membership_no,
				'default_amount':self.due_amt,
				'default_invoice_link':self.id},
				'target': 'new', }


class RegTrainng(models.Model):
	_name = 'struct.training'

	customer = fields.Many2one('res.partner', string="Member", required=True)
	training = fields.Many2one('training.schedule', string="Training Session")
	start_date = fields.Date(string="Start Date")
	end_date = fields.Date(string="End Date")
	trainer = fields.Many2one('hr.employee', string="Trainer")


class RegTrainngShedule(models.Model):
	_name = 'training.schedule'

	name = fields.Char(string="Name", required=True)
	responsible = fields.Many2one('hr.employee', string="Responsible")
	tree_id = fields.One2many('training.schedule.tree', 'train_id')


class RegTrainngSheduleTREE(models.Model):
	_name = 'training.schedule.tree'

	time = fields.Char(string="Time")
	activity = fields.Many2one('struct.training.activity', string="Activity")
	desc = fields.Char(string="Description")
	status = fields.Char(string="Status")
	train_id = fields.Many2one('training.schedule')


class RegActivity(models.Model):
	_name = 'struct.training.activity'

	name = fields.Char(string='Name')


class RegTrainngStatus(models.Model):
	_name = 'training.status'

	date = fields.Date(string="Date")
	trainer = fields.Many2one('hr.employee', string="Trainer")
	status_id = fields.One2many('training.status.tree', 'status_tree')


class RegTrainngStatusTree(models.Model):
	_name = 'training.status.tree'

	member_no = fields.Char(string="Membership No")
	member = fields.Many2one('reg.form', string="Member")
	types = fields.Many2one('status.type', string="Type")
	start_time = fields.Datetime(string="Start Time")
	end_time = fields.Datetime(string="End Time")
	assesment = fields.Boolean(string="Assesment")
	diet_plan = fields.Boolean(string="Diet Plan")
	status_tree = fields.Many2one('training.status')


class RegTrainngStatusType(models.Model):
	_name = 'status.type'

	name = fields.Char(string="Name")


class RegAppoint(models.Model):
	_name = 'struct.appointment'

	name = fields.Char(string='Name')
	mem_name = fields.Many2one('res.partner',string='Name')
	walkin_name = fields.Many2one('res.partner',string='Walkin Customer')
	# book_status = fields.Many2one('book.status',string='Booking Status')
	contact = fields.Char(string='Contact')
	types = fields.Selection(
		[('member', 'Member'), ('walkin', 'Walkin'), ('ref', 'Reference'), ('comp', 'Complimentory')], string="Type",required=True)
	book_status = fields.Selection(
		[('book', 'Booked'), ('avial', 'Availed'), ('cancel', 'Cancelled')], string="Booking Status")
	date = fields.Date(string='Date',default=date.today())
	time = fields.Datetime(string='Appointment Time')
	member_no = fields.Many2one('reg.form', string='Membership No.')
	mamsus_name = fields.Many2one('hr.employee', string='Masseuse Name')
	invoice_link = fields.Many2one('account.invoice', string='Invoice')
	branch = fields.Many2one('branch', string='Branch',readonly=True)
	total = fields.Float('Total Amount',readonly=True)
	discount = fields.Integer('Discount')
	discount_type = fields.Selection([('per', 'Percentage'), ('amt', 'Amount')], string="Discount Type")
	appoint_id = fields.One2many('struct.appointment.tree', 'appoint_tree')
	stages = fields.Selection([
		('draft', 'Draft'),
		('booked', 'Booked'),
		('avail', 'Availed'),
		('cancel', 'Cancelled'),
	], default='draft')

	@api.onchange('appoint_id')
	def get_total(self):
		value = 0
		for x in self.appoint_id:
			value = value + x.subtotal
		self.total = value


	@api.onchange('member_no')
	def get_member_data(self):
		if self.member_no:
			self.mem_name = self.member_no.member_link.id


	@api.multi
	def cancel(self):
		self.stages = 'cancel'

	@api.multi
	def booked(self):
		self.stages = 'booked'

	@api.multi
	def avail(self):
		self.stages = 'avail'


	@api.multi
	def unlink(self):
		for x in self:
			if x.stages == "booked" or x.stages == "avail":
				raise  ValidationError('Cannot Delete Record')
	
		return super(RegAppoint,self).unlink()

	# @api.onchange('discount','discount_type')
	# def get_discount(self):
	# 	if self.discount_type:
	# 		total = 0
	# 		if self.discount_type == 'amt':
	# 			for x in self.appoint_id:
	# 				total = total + x.rates
	# 			self.total = total - self.discount
	# 		if self.discount_type == 'per':
	# 			for x in self.appoint_id:
	# 				total = total + x.rates
	# 			if self.discount <= 100:
	# 				value = total * (self.discount / 100.0)
	# 				self.total = total - value
	# 			else:
	# 				raise ValidationError('Discount Can not be more than 100%')


	@api.onchange('types')
	def get_branch(self):
		if self.types:
			users = self.env['res.users'].search([('id','=',self._uid)])
			self.branch = users.branch.id



	@api.multi
	def create_invoice(self):
		invoice_entries = self.env['account.invoice'].search([])
		if self.types == 'member':
			create_invoice_entry = invoice_entries.create({
						'partner_id': self.mem_name.id,
						'branch': self.branch.id,
						'date_invoice': self.date,
						'membership_no': self.member_no.memship_no,
						'type': 'out_invoice',
					})
		if self.types == 'walkin':
			create_invoice_entry = invoice_entries.create({
						'partner_id': self.walkin_name.id,
						'customer_name': self.name,
						'branch': self.branch.id,
						'date_invoice': self.date,
						'check': True,
						'type': 'out_invoice',

					})

		for y in self.appoint_id:
			a = create_invoice_entry.invoice_line_ids.create({
				'price_unit': y.subtotal,
				'account_id': 27,
				'name': y.types.name,
				'invoice_id': create_invoice_entry.id,
			})

		self.invoice_link = create_invoice_entry.id


# class RegMemberShip(models.Model):
# 	_name = 'member.ship'

# 	name = fields.Char(string='Name')

	# _sql_constraints = [
	# ('name', 'unique(name)','This Membership Number Already Esixts!')
	# ]

class RegMemberShip(models.Model):
	_name = 'book.status'

	name = fields.Char(string='Name')


class RegAppointTree(models.Model):
	_name = 'struct.appointment.tree'

	types = fields.Many2one('types.massage', string='Type')
	duration = fields.Float(string='Duration')
	rates = fields.Float(string='Rates')
	subtotal = fields.Float(string='Sub Total')
	appoint_tree = fields.Many2one('struct.appointment')

	@api.onchange('types')
	def _onchange_types(self):
		if self.types:
			self.rates = self.types.rate

	@api.onchange('rates','duration')
	def get_subtotal(self):
		self.subtotal = self.rates * self.duration


class RegMassage(models.Model):
	_name = 'types.massage'

	name = fields.Char(string='Name')
	rate = fields.Float(string='Rate')


class RegVisitor(models.Model):
	_name = 'struct.visitor'
	
	date = fields.Date(string='Date',required=True)
	time = fields.Datetime(string='Time')
	attend_by = fields.Many2one('hr.employee', string="Attended By")
	name = fields.Char(string='Visitor Name',required=True)
	ref = fields.Many2one('reg.form',string='Reference')
	cmp_name = fields.Char(string='Company Name')
	designation = fields.Char(string='Designation')
	interest_lvl = fields.Integer(string='Interest Level')
	profile_lvl = fields.Integer(string='Profile Level')
	contact = fields.Integer(string='Contact Info')
	approve = fields.Many2one('hr.employee', string="Approved")
	remarks = fields.Text(string='Remarks')
	remarks_on_call = fields.Text(string='Remarks on Call to Visitors')
	curent_date = fields.Date(string="current",compute="compute_monthly")
	plan = fields.Boolean(string="Plan",compute="compute_plan",store=True)
	# req_date = fields.Date(string="required")

	# @api.onchange('date')
	# def required_date(self):
	# 	start_date = datetime.strptime(self.curent_date,"%Y-%m-%d")
	# 	self.req_date = start_date - timedelta(days=30)


	@api.one
	def compute_monthly(self):
		self.curent_date = date.today() - timedelta(days=30)

	@api.one
	def compute_plan(self):
		if self.date >= self.curent_date:
			self.plan = True



class RegVisitorDaily(models.Model):
	_name = 'struct.visitor.daily'

	name = fields.Char(string='Name')


class RegVisitorMonthly(models.Model):
	_name = 'struct.visitor.monthly'

	name = fields.Char(string='Name')


class RegAttend(models.Model):
	_name = 'struct.attend'

	name = fields.Char(string='Name')


class RegAttendReport(models.Model):
	_name = 'struct.attend.report'

	name = fields.Char(string='Name')


class RegJoining(models.Model):
	_name = 'struct.joining'

	name = fields.Char(string='Name')


class RegReJoining(models.Model):
	_name = 'struct.rejoining'
	_rec_name = 'member'

	date = fields.Date(string='Date',required=True)
	rejoining = fields.Date(string='Date of Rejoining')
	change_pack_date = fields.Date(string='Date of Change Package')
	membership_no = fields.Many2one('reg.form',string='Membership No.')
	membership_no_ch = fields.Many2one('reg.form',string='Membership No.')
	member = fields.Many2one('res.partner',string='Member Name')
	package = fields.Many2one('reg.package',string='Current Package',readonly=True)
	change_package = fields.Many2one('reg.package',string='New Package',required=True)
	invoice_link = fields.Many2one('account.invoice')
	service = fields.Char(string='Current Service',readonly=True)
	new_service = fields.Many2many('struct.service',string='New Service',required=True)
	change = fields.Boolean(string='Change')
	branch = fields.Many2one('branch',string='Branch',readonly=True)
	payment_terms = fields.Many2one('account.payment.term',string='Payment Terms')
	advance = fields.Float(string='Advance')
	total = fields.Float(string='Total',readonly=True)
	discount = fields.Integer(string='Discount')
	discount_amt = fields.Float(string='Discounted Amount',readonly=True)
	discount_type = fields.Selection([('per', 'Percentage'), ('amt', 'Amount')], string="Discount Type")
	morning = fields.Boolean(string="Morning")
	noon = fields.Boolean(string="Noon")
	afternoon = fields.Boolean(string="Afternoon")
	show_mem = fields.Boolean(string="Show",compute="compute_show_fields")
	result = fields.Boolean(string="result",compute="compute_result")
	evening = fields.Boolean(string="Evening")
	time_slot_m = fields.Many2one('struct.slots',string="Time Slot")
	time_slot_n = fields.Many2one('struct.slots',string="Time Slot")
	time_slot_af = fields.Many2one('struct.slots',string="Time Slot")
	time_slot_e = fields.Many2one('struct.slots',string="Time Slot")
	stages = fields.Selection([
		('draft', 'Draft'),
		('invoiced', 'Invoiced'),
		('cancel', 'Cancelled'),
		('validate', 'Validate'),
	], default='draft')



	@api.onchange('membership_no','membership_no_ch')
	def get_discount(self):
		if self.change == False:
			if self.membership_no:
				self.service = False
				value = 0
				ser = []
				users = self.env['res.users'].search([('id','=',self._uid)])
				self.branch = users.branch.id
				self.package = self.membership_no.package.id
				self.member = self.membership_no.member_link.id
				self.payment_terms = self.membership_no.payment_terms.id
				for x in self.membership_no.service:
					ser.append(x.name)
				for z in ser:
					if self.service:
						self.service = self.service + ',' + z
					if not self.service:
						self.service = z
				self.membership_no.write({'rejoining':self.date})
		if self.change == True:
			if self.membership_no_ch:
				self.service = False
				value = 0
				ser = []
				users = self.env['res.users'].search([('id','=',self._uid)])
				self.branch = users.branch.id
				self.member = self.membership_no_ch.member_link.id
				self.package = self.membership_no_ch.package.id
				self.payment_terms = self.membership_no_ch.payment_terms.id
				for x in self.membership_no_ch.service:
					ser.append(x.name)
				for z in ser:
					if self.service:
						self.service = self.service + ',' + z
					if not self.service:
						self.service = z
				self.membership_no_ch.write({'rejoining':self.date})

			# if self.rejoining:
			# 	value = datetime.strptime(self.rejoining,'%Y-%m-%d').strftime('%d')
				




	@api.onchange('change_package', 'new_service')
	def get_total_rejoin(self):
		if self.change_package:
			self.total = self.change_package.reg_fee
			for x in self.new_service:
				for y in self.change_package.pakg_tree:
					if x.name == y.service.name:
						self.total = self.total + y.amount
						
			


	@api.onchange('discount', 'total', 'discount_type')
	def get_discount_rejoin(self):
		if self.discount_type and self.total > 0:
			if self.discount_type == 'amt':
				self.discount_amt = self.total - self.discount
			if self.discount_type == 'per':
				if self.discount <= 100:
					value = self.total * (self.discount / 100.0)
					self.discount_amt = self.total - value
				else:
					raise ValidationError('Discount Can not be more than 100%')



	@api.onchange('morning')
	def select_one(self):
		if self.morning == True:
			self.noon = False
			self.afternoon = False
			self.evening = False
			self.time_slot_m = False

	@api.onchange('noon')
	def select_one1(self):
		if self.noon == True:
			self.morning = False
			self.afternoon = False
			self.evening = False
			self.time_slot_n = False

	@api.onchange('afternoon')
	def select_one2(self):
		if self.afternoon == True:
			self.morning = False
			self.noon = False
			self.evening = False
			self.time_slot_af = False

	@api.onchange('evening')
	def select_one3(self):
		if self.evening == True:
			self.morning = False
			self.noon = False
			self.afternoon = False
			self.time_slot_e = False
			

	@api.multi
	def validate(self):
		if self.change == False:
			if self.membership_no:
				self.stages = 'validate'
				self.membership_no.stages = 'member'
				self.membership_no.package = self.change_package.id
				self.membership_no.service = self.new_service
				self.membership_no.total = self.total
				self.membership_no.discount = self.discount
				self.membership_no.payment_terms = self.payment_terms.id
				self.membership_no.discount_type = self.discount_type
				self.membership_no.discount_amt = self.discount_amt
				if self.morning:
					self.membership_no.morning = self.morning
					self.membership_no.time_slot_m = self.time_slot_m.id
				if self.noon:
					self.membership_no.noon = self.noon
					self.membership_no.time_slot_n = self.time_slot_n.id
				if self.afternoon:
					self.membership_no.afternoon = self.afternoon
					self.membership_no.time_slot_af = self.time_slot_af.id
				if self.evening:
					self.membership_no.evening = self.evening
					self.membership_no.time_slot_e = self.time_slot_e.id

				# self.membership_no.write({'package':self.change_package.id,'service':self.new_service})
				# if self.new_service:
				# 	self.membership_no.write({'service':self.new_service})

		if self.change == True:
			if self.membership_no_ch:
				self.stages = 'validate'
				self.membership_no_ch.package = self.change_package.id
				self.membership_no_ch.service = self.new_service
				self.membership_no_ch.total = self.total
				self.membership_no_ch.discount = self.discount
				self.membership_no_ch.payment_terms = self.payment_terms.id
				self.membership_no_ch.discount_type = self.discount_type
				self.membership_no_ch.discount_amt = self.discount_amt
				if self.morning:
					self.membership_no_ch.morning = self.morning
					self.membership_no_ch.time_slot_m = self.time_slot_m.id
				if self.noon:
					self.membership_no_ch.noon = self.noon
					self.membership_no_ch.time_slot_n = self.time_slot_n.id
				if self.afternoon:
					self.membership_no_ch.afternoon = self.afternoon
					self.membership_no_ch.time_slot_af = self.time_slot_af.id
				if self.evening:
					self.membership_no_ch.evening = self.evening
					self.membership_no_ch.time_slot_e = self.time_slot_e.id



	@api.multi
	def cancel(self):
		self.stages = 'cancel'
		self.invoice_link.unlink()


	@api.one
	def compute_show_fields(self):
		if self.invoice_link:
			if self.invoice_link.stages != 'draft':
				if self.invoice_link.due_amt != self.invoice_link.amount_total:
					self.show_mem = True

	@api.one
	def compute_result(self):
		if self.invoice_link:
			if self.stages == 'invoiced' and self.show_mem == True:
				self.result = True


	@api.multi
	def create_invoice(self):
		self.stages = 'invoiced'
		value = 0
		discount = " "
		if re.findall('([0-9]+)', self.payment_terms.name):
			pay = int(re.findall('([0-9]+)', self.payment_terms.name)[0])
		else:
			pay = 0
		if self.change == False:
			if self.invoice_link:
				self.invoice_link.unlink()
	
			invoice_entries = self.env['account.invoice'].search([])
			create_invoice_entry = invoice_entries.create({
									'partner_id': self.member.id,
									'branch': self.branch.id,
									'membership_no': self.membership_no.memship_no,
									'date_invoice': self.date,
									'payment_term_id': self.payment_terms.id,
									'due_date': datetime.now() + timedelta(days=pay),
									'rejoin': True,
									'type': 'out_invoice',
								})

			b = create_invoice_entry.invoice_line_ids.create({
				'price_unit': self.change_package.reg_fee,
				'account_id': self.change_package.accounts.id,
				'name': 'Membership Fee',
				'invoice_id': create_invoice_entry.id,
			})

			for x in self.new_service:
				for y in self.change_package.pakg_tree:
					if x.name == y.service.name:
						a = create_invoice_entry.invoice_line_ids.create({
							'price_unit': y.amount,
							'account_id': y.pakg_id.accounts.id,
							'name': y.service.name,
							'invoice_id': create_invoice_entry.id,
						})

			if self.discount > 0:

				if self.discount_type == 'amt' and self.discount:
						value = (self.discount) * -1.0
						discount = str(self.discount) + 'Rs' 
				if self.discount_type == 'per' and self.discount:
					value = (self.total - self.discount_amt) * -1.0
					discount = str(self.discount) + '%'

				c = create_invoice_entry.invoice_line_ids.create({
					'price_unit': value,
					'account_id': self.change_package.accounts.id,
					'name': 'Discount' + ' ' + str(discount),
					'invoice_id': create_invoice_entry.id,
				})

			self.invoice_link = create_invoice_entry.id


		if self.change == True:
			if self.invoice_link:
				self.invoice_link.unlink()
			if self.package != self.change_package:
				rec = self.env['account.invoice'].search([('partner_id','=',self.member.id),('stages','in','draft')])
				if rec:
					rec.unlink()
					invoice_entries = self.env['account.invoice'].search([])
					create_invoice_entry = invoice_entries.create({
											'partner_id': self.member.id,
											'branch': self.branch.id,
											'membership_no': self.membership_no_ch.memship_no,
											'date_invoice': self.date,
											'payment_term_id': self.payment_terms.id,
											'due_date': datetime.now() + timedelta(days=pay),
											'rejoin': True,
											'type': 'out_invoice',
										})

					b = create_invoice_entry.invoice_line_ids.create({
						'price_unit': self.change_package.reg_fee,
						'account_id': self.change_package.accounts.id,
						'name': 'Membership Fee',
						'invoice_id': create_invoice_entry.id,
					})

					for x in self.new_service:
						for y in self.change_package.pakg_tree:
							if x.name == y.service.name:
								a = create_invoice_entry.invoice_line_ids.create({
									'price_unit': y.amount,
									'account_id': y.pakg_id.accounts.id,
									'name': y.service.name,
									'invoice_id': create_invoice_entry.id,
								})

					if self.discount > 0:

						if self.discount_type == 'amt' and self.discount:
								value = (self.discount) * -1.0
								discount = str(self.discount) + 'Rs' 
						if self.discount_type == 'per' and self.discount:
							value = (self.total - self.discount_amt) * -1.0
							discount = str(self.discount) + '%'

						c = create_invoice_entry.invoice_line_ids.create({
							'price_unit': value,
							'account_id': self.change_package.accounts.id,
							'name': 'Discount' + ' ' + str(discount),
							'invoice_id': create_invoice_entry.id,
						})

					self.invoice_link = create_invoice_entry.id

				else:

					raise  ValidationError('U Cannot Change Package Now')

			else:
				record_ser = self.env['account.invoice'].search([('partner_id','=',self.member.id),('stages','!=','draft')])
				if record_ser:
					serv1 = []
					balance = 0
					num = datetime.strptime(self.membership_no_ch.last_date, "%Y-%m-%d")
					num1= datetime.strptime(self.date, "%Y-%m-%d")
					days = abs((num1 - num).days)
					service = self.service.split(",")
					for x in self.new_service:
						serv1.append(x.name)
					if len(serv1) > len(service):
						for q in service:
							if q not in serv1:
								raise  ValidationError('You Cannot Reduce Existing Service')
						for z in serv1:
							if z not in service:
								for b in self.package.pakg_tree:
									if z == b.service.name:
										balance = (b.amount / 30) * days
										invoice_entries = self.env['account.invoice'].search([])
										create_invoice_entry = invoice_entries.create({
																'partner_id': self.member.id,
																'branch': self.branch.id,
																'membership_no': self.membership_no_ch.memship_no,
																'date_invoice': self.date,
																'payment_term_id': self.payment_terms.id,
																'due_date': datetime.now() + timedelta(days=pay),
																'rejoin': True,
																'type': 'out_invoice',
															})

										b = create_invoice_entry.invoice_line_ids.create({
											'price_unit': balance,
											'account_id': self.change_package.accounts.id,
											'name': 'New Service ' + z,
											'invoice_id': create_invoice_entry.id,
										})


										self.invoice_link = create_invoice_entry.id

				else:
					for x in record_ser:
						x.unlink()
					invoice_entries = self.env['account.invoice'].search([])
					create_invoice_entry = invoice_entries.create({
											'partner_id': self.member.id,
											'branch': self.branch.id,
											'membership_no': self.membership_no_ch.memship_no,
											'date_invoice': self.date,
											'payment_term_id': self.payment_terms.id,
											'due_date': datetime.now() + timedelta(days=pay),
											'rejoin': True,
											'type': 'out_invoice',
										})

					b = create_invoice_entry.invoice_line_ids.create({
						'price_unit': self.change_package.reg_fee,
						'account_id': self.change_package.accounts.id,
						'name': 'Membership Fee',
						'invoice_id': create_invoice_entry.id,
					})

					for x in self.new_service:
						for y in self.change_package.pakg_tree:
							if x.name == y.service.name:
								a = create_invoice_entry.invoice_line_ids.create({
									'price_unit': y.amount,
									'account_id': y.pakg_id.accounts.id,
									'name': y.service.name,
									'invoice_id': create_invoice_entry.id,
								})

					if self.discount > 0:

						if self.discount_type == 'amt' and self.discount:
								value = (self.discount) * -1.0
								discount = str(self.discount) + 'Rs' 
						if self.discount_type == 'per' and self.discount:
							value = (self.total - self.discount_amt) * -1.0
							discount = str(self.discount) + '%'

						c = create_invoice_entry.invoice_line_ids.create({
							'price_unit': value,
							'account_id': self.change_package.accounts.id,
							'name': 'Discount' + ' ' + str(discount),
							'invoice_id': create_invoice_entry.id,
						})

					self.invoice_link = create_invoice_entry.id


	@api.model
	def create(self, vals):
		new_record = super(RegReJoining, self).create(vals)
		if new_record.morning == False and new_record.noon == False and new_record.evening == False and new_record.afternoon == False:
			raise  ValidationError('Select Timeslot')
		


		return new_record



class RegContinue(models.Model):
	_name = 'struct.continue'

	name = fields.Char(string='Name')


class RegDisContinue(models.Model):
	_name = 'struct.discontinue'

	name = fields.Char(string='Name')


class RegPaid(models.Model):
	_name = 'struct.paid'

	name = fields.Char(string='Name')


class RegUnPaid(models.Model):
	_name = 'struct.unpaid'

	name = fields.Char(string='Name')


class RegService(models.Model):
	_name = 'struct.service'

	name = fields.Char(string='Name')
	

class RegPackage(models.Model):
	_name = 'reg.package'

	name = fields.Char(string='Name', required=True)
	month = fields.Integer(string='Months', required=True)
	reg_fee = fields.Float(string='Registration Fee', required=True)
	accounts = fields.Many2one('account.account',string='Account', required=True)
	pakg_tree = fields.One2many('reg.package.tree', 'pakg_id')


class RegPackageTree(models.Model):
	_name = 'reg.package.tree'

	service = fields.Many2one('struct.service', string="Services", required=True)
	amount = fields.Float(string="Amount")
	pakg_id = fields.Many2one('reg.package')


# class RegServiceTree(models.Model):
#     _name = 'service.package'

#     name = fields.Char(string='name')

class RegTrainer(models.Model):
	_name = 'struct.trainer'

	name = fields.Char(string='Name')


class RegSlots(models.Model):
	_name = 'struct.slots'
	_rec_name = 'name'

	start_time = fields.Char(string='Start Time')
	end_time = fields.Char(string='End Time')
	name = fields.Char(string='Name')
	training = fields.Boolean(string='Training')
	time_slot = fields.Selection([
		('morning', 'Morning'),
		('noon', 'Noon'),
		('afternoon', 'Afternoon'),
		('evening', 'Evening'),
	])

	@api.onchange('start_time', 'end_time')
	def time_schedule(self):
		self.name = "%s %s %s" % (self.start_time or '', " - ", self.end_time or '')


class RegBranches(models.Model):
	_name = 'struct.branches'

	name = fields.Char(string='Name')


class RegVisitorType(models.Model):
	_name = 'struct.visit.type'

	name = fields.Char(string='Name')


class employee_extend(models.Model):
	_inherit = 'hr.employee'

	massus = fields.Boolean(string="Masseuse") 
	trainer = fields.Boolean(string="Trainer")
	branch = fields.Many2one('branch',string="Branch")


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	trainer = fields.Boolean(string='Trainier')

class PartnerExtend(models.Model):
	_inherit = 'res.partner'

	walkin = fields.Boolean(string='Walkin Customer')

	@api.onchange('walkin')
	def change(self):
		if self.walkin == True:
			self.customer = False


class struct_user_extend(models.Model):
	_inherit  = 'res.users'
	branch = fields.Many2one ('branch',string="Branch")


class branchAAA(models.Model):
	_name = 'branch'

	address = fields.Char(string="Address")
	name = fields.Char(string="Name")
	phone = fields.Char(string="Phone")
	mobile = fields.Char(string="Mobile")


class journal_extend(models.Model):
	_inherit = 'account.journal'

	branch      = fields.Many2one('branch',string="Branch")

class invoice_extend(models.Model):
	_inherit = 'account.invoice.line'

	namea      = fields.Char(string="Branch")

# class bank_extend(models.Model):
#     _inherit = 'account.bank.statement'

#     branch      = fields.Many2one('branch',string="Branch")

#     @api.onchange('journal_id')
#     def get_branch(self):
#         records = self.env['account.journal'].search([('id','=',self.journal_id.id)])
#         self.branch = records.branch.id

# class bank_extend(models.Model):
#     _inherit = 'account.bank.statement.line'

#     @api.multi
#     def process_reconciliation(self,data,uid,id):
#         new_record = super(bank_extend, self).process_reconciliation(data,uid,id)
#         records = self.env['account.bank.statement'].search([('id','=',self.statement_id.id)])
#         journal_entery =  self.env['account.move'].search([], order='id desc', limit=1)
#         journal_entery.branch = records.branch.id
#         return new_record


# class move_extend(models.Model):
#     _inherit = 'account.move'

#     branch      = fields.Many2one('branch',string="Branch")

class RegSale(models.Model):
	_name = 'struct.sale'

	name = fields.Many2one('res.partner',string='Customer Name')
	membership_no = fields.Many2one('reg.form',string='Membership No.',required=True)
	date = fields.Date(string='Date',default=date.today())
	subtotal = fields.Float()
	show_mem = fields.Boolean(string="Show",compute="compute_show_fields")
	branch = fields.Many2one('branch', string='Branch',readonly=True)
	invoice_link = fields.Many2one('account.invoice')
	waking_ref_mem = fields.Char(string='Walking Ref Member')
	sale_id = fields.One2many('struct.sale.tree','sale_tree')
	stages = fields.Selection([
		('draft', 'Draft'),
		('invoice', 'Invoiced'),
		('validate', 'Validate'),
	], default='draft')


	@api.onchange('sale_id')
	def get_subtotal(self):
		value = 0
		for x in self.sale_id:
			value = value + x.subtotal
		self.subtotal = value


	@api.onchange('membership_no')
	def get_customer(self):
		users = self.env['res.users'].search([('id','=',self._uid)])
		if self.membership_no:
			self.name = self.membership_no.member_link.id
			self.branch = users.branch.id


	@api.one
	def compute_show_fields(self):
		if self.invoice_link:
			if self.invoice_link.stages != 'draft':
				if self.invoice_link.due_amt == 0:
					self.show_mem = True

	@api.multi
	def unlink(self):
		for x in self:
			if x.stages == "invoice" or x.stages == "validate":
				raise  ValidationError('Cannot Delete Record')
	
		return super(RegSale,self).unlink()


	@api.multi
	def validate(self):
		self.stages = "validate"


			

class RegSaleTree(models.Model):
	_name = 'struct.sale.tree'


	product = fields.Many2one('product.template',string='Product')
	qty = fields.Integer(string='Quantity')
	price = fields.Float(string='Price')
	subtotal = fields.Float(string='Sub Total')
	sale_tree = fields.Many2one('struct.sale')

	@api.onchange('qty','price')
	def grt_subtotal(self):
		self.subtotal = self.qty * self.price


class RegPurchase(models.Model):
	_name = 'struct.purchase'

	name = fields.Many2one('res.partner',string='Customer Name')
	membership_no = fields.Many2one('reg.form',string='Membership No.')
	date = fields.Date(string='Date',default=date.today())
	subtotal = fields.Float()
	waking_ref_mem = fields.Char(string='Walking Ref Member')
	purchase_id = fields.One2many('struct.purchase.tree','purchase_tree')
	stages = fields.Selection([
		('draft', 'Draft'),
		('invoice', 'Invoiced'),
		('validate', 'Validate'),
	], default='draft')


	@api.onchange('purchase_id')
	def get_subtotal(self):
		value = 0
		for x in self.purchase_id:
			value = value + x.subtotal
		self.subtotal = value


	@api.onchange('membership_no')
	def get_customer(self):
		if self.membership_no:
			self.name = self.membership_no.member_link.id


class RegPurchaseTree(models.Model):
	_name = 'struct.purchase.tree'


	product = fields.Many2one('product.template',string='Product')
	qty = fields.Integer(string='Quantity')
	price = fields.Float(string='Price')
	subtotal = fields.Float(string='Sub Total')
	purchase_tree = fields.Many2one('struct.purchase')

	@api.onchange('qty','price')
	def grt_subtotal(self):
		self.subtotal = self.qty * self.price



class StockExtend(models.Model):
	_inherit = 'product.template'

	total_sale = fields.Float(string='Total Sale')
	total_purchase = fields.Float(string='Total Purchase')
	remaining = fields.Float(string='Remaining')

class Confirm(models.Model):
	_name = 'confirm'

	reg_link = fields.Many2one('reg.form')


	@api.multi
	def confirm(self):
		self.reg_link.stages = "non_member"

class InvoiceWizard(models.Model):
	_name = 'invoice.wizard'

	@api.multi
	def sent_for_clearance(self):
		active_class = self.env['struct.sale'].browse(self._context.get('active_ids'))
		if active_class:
			for x in active_class:
				if x.stages == "draft":
					x.stages = 'invoice'
					invoice_entries = self.env['account.invoice'].search([])
					create_invoice_entry = invoice_entries.create({
							'partner_id': x.name.id,
							'branch': x.branch.id,
							'date_invoice': x.date,
							'membership_no':x.membership_no.memship_no,
							'type': 'out_invoice',

						})

					for y in x.sale_id:
						a = create_invoice_entry.invoice_line_ids.create({
							'price_unit': y.subtotal,
							'account_id': 27,
							'name': y.product.name,
							'invoice_id': create_invoice_entry.id,
						})

					x.invoice_link = create_invoice_entry.id







