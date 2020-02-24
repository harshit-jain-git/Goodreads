import random
import string

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def main():
	# out = open('book_tags_.csv', 'w')
	# with open('book_tags.csv', 'r') as file:
	# 	l = file.readline()
	# 	for line in file:
	# 		l1 = l.split(',')
	# 		l2 = line.split(',')
	# 		if (l1[0] == l2[0] and l1[1] == l2[1]):
	# 			pass
	# 		else:
	# 			out.write(line)

	# 		l = line

	user_file = open("users.csv", 'w')
	# user_id = {}

	# count = 0
	# with open('ratings.csv') as file:
	# 	file.readline()
	# 	for line in file:
	# 		count += 1
	# 		if (count%100000 == 0):
	# 			print(count)
	# 		user = line.split(',')[0]
	# 		if user not in user_id.keys():
	# 			user_id[user] = 0
	# 			user_file.write(user + ',' + randomString() + '\n')

	# with open('to_read.csv') as file:
	# 	file.readline()
	# 	for line in file:
	# 		user = line.split(',')[0]
	# 		if user not in user_id.keys():
	# 			user_id[user] = 0
	# 			user_file.write(user + ',' + randomString() + '\n')

	for i in range(1, 53425):
		user_file.write(str(i) + ',' + randomString() + '\n')

	user_file.close()

if __name__ == '__main__':
	main()