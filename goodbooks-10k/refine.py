def main():
	out = open('book_tags_.csv', 'w')
	with open('book_tags.csv', 'r') as file:
		l = file.readline()
		for line in file:
			l1 = l.split(',')
			l2 = line.split(',')
			if (l1[0] == l2[0] and l1[1] == l2[1]):
				pass
			else:
				out.write(line)

			l = line

if __name__ == '__main__':
	main()