//---------------------------------------------------------------------------------------
// Exception class
// 
// File:   cexcept.h
//---------------------------------------------------------------------------------------


#ifndef _CEXCEPT_H
#define _CEXCEPT_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef __EXCEPTION__ // from <exception> include file
// use C++ std exception class
class cExcept : public std::exception
#else
class cExcept
#endif
{
	public:
		cExcept(const char* const file, const int line, const char* const message=0) :
			_file(const_cast<char*>(file)),
			_line(line)
		{
			_text[0] = 0;
			if(message != 0)
				::snprintf(_text, sizeof(_text), "%s", message);
		}

		cExcept(const char* const file, const int line, const char* const message,
			   	const char* const extra) :
			_file(const_cast<char*>(file)),
			_line(line)
		{
			::snprintf(_text, sizeof(_text), "%s [%s]", message, extra!=NULL?extra:"NULL");
		}

		cExcept(const char* const file, const int line, const char* const message,
			   	const int arg) :
			_file(const_cast<char*>(file)),
			_line(line)
		{
			::snprintf(_text, sizeof(_text), "%s %d", message, arg);
		}

		cExcept(const char* const file, const int line, const char* const message,
			   	const char* const extra, const int arg1, const int arg2) :
			_file(const_cast<char*>(file)),
			_line(line)
		{
			::snprintf(_text, sizeof(_text), "%s [%s] %d %d", message, extra!=NULL?extra:"NULL", arg1, arg2);
		}

		static void exitApplication()
	   	{
			// make sure exit is only called once
			static bool first_time_called = true;
			if(first_time_called)
			{
				first_time_called = false;
				//printf("exit() called first_time_called=%d\n", first_time_called);
			   	::exit(1);
			}
		}

		const char* format()
	   	{
		   static const char* const fmt = "Exception! %s [%s:%d]";
		   return fmt;
		}
		const char * getFile() const { return _file; }
		const int getLine() const { return _line; }
		const char * getText() const { return _text; }
    
        // from the <exception> header file:
        // Returns a C-style character string describing the general cause of the current error.
        virtual const char* what() const throw() { return _text; }

		// set the filename and line number for re-throws
		cExcept& setFileLine(const char* const file, const int line)
		{
			// append the current file and line number to _text before reassigning.
			int len = ::strlen(_text);
			::snprintf(&_text[len], sizeof(_text)-len-1, " [%s:%d]", _file, _line);
			_file = const_cast<char*>(file);
			_line = line;
			return *this;
		}

	protected:
		char* _file;
		int   _line;
		char  _text[1000];

	private:
		cExcept(); // do not allow default construction
};


// No Memory Exception
class cExceptNoMemory : public cExcept
{
	public:
		cExceptNoMemory(const char* const file, const int line, const char* const message="No Memory") :
		   	cExcept(file, line, message) { }
};


#endif // _CEXCEPT_H

