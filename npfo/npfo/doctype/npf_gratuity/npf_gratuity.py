# Copyright (c) 2025, MD Kaleem  and contributors
# For license information, please see license.txt


from frappe.utils import getdate, today, date_diff, flt
from collections import defaultdict

import frappe
from frappe.model.document import Document



class NPFGratuity(Document):


	def before_insert(self):
		"""
		This function calculates the gratuity amount for an employee before inserting the record.
		The calculation is based on:
		- The employee's date of joining.
		- The last drawn basic pay.
		- The number of leave without pay (LWP) days.
		- The number of years worked.
		- The first 3 years providing 15 days of gratuity per year.
		- The remaining years providing 30 days of gratuity per year.
		"""
		# Fetch Employee Document
		employee_doc = frappe.get_doc("Employee", self.employee)
		if  employee_doc.custom_nationlity !="Oman":
		# Set Salary Component for Gratuity
			self.salary_component = "Gratuity Pay"


			# Validate Employee Selection
			if not employee_doc:
				frappe.throw("Please Select a Proper Employee")

			# Validate if Date of Joining is Set
			if not employee_doc.date_of_joining:
				frappe.throw("Date of Joining is not set for the selected Employee")

			# Get Employee Joining Date and End of Service Date (Today)
			joining_date = getdate(employee_doc.date_of_joining)
			end_of_service_date = getdate(today())

			# Calculate Total Days Worked (Including the Last Day)
			total_days_worked = date_diff(end_of_service_date, joining_date) + 1

			# Fetch Leave Without Pay (LWP) Records for the Employee
			leave_records = frappe.get_all(
				"Leave Application", 
				filters={"leave_type": "Leave Without Pay", "employee": self.employee}, 
				fields=["from_date", "to_date"]
			)

			# Calculate Total Unpaid Leave Days
			total_unpaid_days = sum(
				(date_diff(getdate(record["to_date"]), getdate(record["from_date"])) + 1) 
				for record in leave_records
			)

			# Calculate Actual Worked Days (Subtracting Unpaid Leave Days)
			actual_worked_days = total_days_worked - total_unpaid_days

			# Convert Actual Worked Days to Years of Service
			self.current_work_experience = flt(actual_worked_days / 365, 2)  # Rounded to 2 decimal places

			# Fetch the Last Drawn Basic Pay from Custom Earnings
			basic_pay = next(
				(amount.amount for amount in employee_doc.custom_earnings if amount.salary_component == "Basic Pay"), 0
			)

			# Validate if Basic Pay is Set
			if basic_pay <= 0:
				frappe.throw("Basic Pay is not set for the selected Employee")

			# Initialize Gratuity Amount
			gratuity_amount = 0

			# Check if Employee has Completed at Least 1 Year of Service
			if self.current_work_experience < 1:
				self.custom_amount = 0  # No gratuity for less than 1 year
			else:
				# Split Gratuity Calculation into First 3 Years and Remaining Years
				first_3_years = min(3, self.current_work_experience)  # Max 3 years
				remaining_years = max(0, self.current_work_experience - 3)  # Years beyond 3

				# Calculate Gratuity for First 3 Years (15 Days per Year)
				gratuity_amount += (first_3_years * (basic_pay / 30) * 15)

				# Calculate Gratuity for Remaining Years (30 Days per Year)
				gratuity_amount += (remaining_years * (basic_pay / 30) * 30)

				# Store Final Gratuity Amount (Rounded to 2 Decimal Places)
				self.custom_amount = flt(gratuity_amount, 2)


	def on_submit(self):
		new_additional_salary = frappe.new_doc("Additional Salary")
		new_additional_salary.update({
			"employee":self.employee,
			"company":self.company,
			"payroll_date":self.payroll_date,
			"salary_component":"Gratuity Pay",
			"currency":"AED",
			"amount": self.custom_amount,
			"docstatus":1

		})
		new_additional_salary.insert()
		frappe.db.commit()
