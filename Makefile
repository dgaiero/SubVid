# the compiler: gcc for C program, define as g++ for C++
  CC = pyinstaller

  # compiler flags:
  #  -g    adds debugging information to the executable file
  #  -Wall turns on most, but not all, compiler warnings
  CFLAGS  = --icon=default_icon.ico --noconsole -y

  # the build target executable:
  TARGET = SubVid
  ARTIFACTS = build dist

  all: $(TARGET)

  $(TARGET): $(TARGET).py
	$(CC) $(CFLAGS) $(TARGET).py

#   preview:

# 	$(TARGET): $(TARGET).py
# 	pipenv shell
# 	python $(TARGET).py

  clean:
	$(RM) $(TARGET).spec
	$(RM) -rf $(ARTIFACTS)