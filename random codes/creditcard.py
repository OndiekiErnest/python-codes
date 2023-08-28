
from stdiomask import getpass
class CreditCard:
	"""A Bank Credit Card"""
	def __init__(self, customer, bank, acc, limit, bal=0):
		self._customer = customer
		self._bank = bank
		self._account = acc
		self._limit = limit
		try:
			self._balance = int(str(bal).strip('-'))
		except ValueError:
			print("Account balance entered must be an integer.")
			self._balance = 0

	def charge(self, amt):
		try:
			amt = int(str(amt).strip('-'))
			if amt + self._balance > self._limit:
				return f"{self._limit} credit limit exceeded."
			else:
				self._balance += amt
				return True
		except ValueError:
			return "Charge amount must be an integer."

	def make_payment(self, amount):
		try:
			amount = int(str(amount).strip('-'))
			if amount <= self._balance:
				self._balance -= amount
				return True
			else:
				return "Insufficient balance. Recharge and try again."
		except ValueError:
			return "Payment amount must be an integer."

	def get_customer(self):
		"""Return customer full name"""
		return self._customer

	def get_account(self):
		"""Return customer's account number (str)"""
		return self._account

	def get_bank(self):
		"""Return bank's name"""
		return self._bank

	def get_limit(self):
		"""Return customer's current credit limit"""
		return self._limit

	def get_balance(self):
		"""Return current balance"""
		return self._balance

if __name__ == '__main__':
	wallet = []
	wallet.append(CreditCard('John Bowman', 'Equity Bank',
	 				'5391 0375 9387 5309', 2500, "good"))
	wallet.append(CreditCard('John Bowman', 'Kenya Commercial Bank',
	 				'3485 0399 3395 1954', 3500))
	wallet.append(CreditCard('John Bowman', 'Barclays Bank',
					'5391 0375 9387 5309', 5000))
	for i in wallet:
		print(i.charge(201))
		print(i.get_balance())

	