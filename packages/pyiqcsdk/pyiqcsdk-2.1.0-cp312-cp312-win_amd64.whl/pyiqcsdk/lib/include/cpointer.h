//---------------------------------------------------------------------------------------
// Template classes which hold pointers
// 
// File:   cpointer.h
//---------------------------------------------------------------------------------------

#ifndef _CPOINTER_H
#define _CPOINTER_H

#include "cexcept.h"

//#define ATOMIC_ADD(x, y) asm volatile("lock add %1, %0" :"=m" (x) :"g" (y))
#define ATOMIC_INC(x) __sync_add_and_fetch((x), 1)
#define ATOMIC_DEC(x) __sync_sub_and_fetch((x), 1)

//---------------------------------------------------------------------------------------
// This template will hold a pointer to a C malloc'd block of type T
// Memory will be free'd with the C free function
//---------------------------------------------------------------------------------------
template<class T>
class cMallocPtr
{
	public:
		cMallocPtr() : _ptr(0) { }
		cMallocPtr(T* p) : _ptr(p) { }
		virtual ~cMallocPtr() { assign(0); }

		// assignment operators
		cMallocPtr<T>& operator=(T* p) {
			assign(p);
			return *this;
		}

		// conversion operators
		operator T* () const { return _ptr; }
		operator T& () const { return *_ptr; }

		// reference operators
		T* operator->() const { return _ptr; }
		T& operator*() const { return *_ptr; }

		T* get() const { return _ptr; }
		bool isNull() const { return _ptr == 0; }
		bool notNull() const { return _ptr != 0; }

		// free the pointer
		void reset() { assign(0); }

		// release - forget the pointer and return it to the caller
		T* release() { 
			T* p = _ptr;
			_ptr = 0;
			return p;
		}

	protected:
// The following should never be used!!!
		cMallocPtr<T>(const cMallocPtr<T>& rhs);
		cMallocPtr<T>& operator=(const cMallocPtr<T>& rhs);
// ---
		void assign(T* p) {
			if(p != _ptr) {
				if(_ptr != 0) {
					::free(_ptr);
				}
				_ptr = p;
			}
		}

	private:
		T* _ptr;
};


//---------------------------------------------------------------------------------------
// This template will hold a pointer to a non-reference counted object
//---------------------------------------------------------------------------------------
template<class T>
class cPtr
{
	public:
		cPtr() : _ptr(0) { }
		cPtr(T* p) : _ptr(p) { }
		virtual ~cPtr() { assign(0); }

		// assignment operators
		cPtr<T>& operator=(T* p) {
			assign(p);
			return *this;
		}

		// conversion operators
		operator T* () const { return _ptr; }
		operator T& () const { return *_ptr; }

		// reference operators
		T* operator->() const { return _ptr; }
		T& operator*() const { return *_ptr; }
		T& operator[](const unsigned int i) const { return _ptr[i]; }
		T& operator[](const int i) const { return _ptr[i]; }

		T* get() const { return _ptr; }
		bool isNull() const { return _ptr == 0; }
		bool notNull() const { return _ptr != 0; }

		// free the pointer
		void reset() { assign(0); }

		// release - forget the pointer and return it to the caller
		T* release() {
			T* p = _ptr;
			_ptr = 0;
			return p;
		}

	protected:
// The following should never be used!!!
		cPtr(const cPtr<T>& rhs);
		cPtr<T>& operator=(const cPtr<T>& rhs);
// ---
		void assign(T* p) {
			if(p != _ptr) {
				if(_ptr != 0) {
					delete _ptr;
				}
				_ptr = p;
			}
		}

	private:
		T* _ptr;
};


//---------------------------------------------------------------------------------------
// This template will hold a pointer to a reference counted object
//---------------------------------------------------------------------------------------
template<class T>
class cCountedPtr
{
	public:
		cCountedPtr<T>() : _counter(0), _ptr(0) { }
		cCountedPtr<T>(const T* const p) : _counter(0), _ptr(const_cast<T*>(p))
	   	{
			if(p != 0)
			{
				_counter = new unsigned int;
				(*_counter) = 1;
			}
			check_state(__LINE__);
	   	}
		cCountedPtr<T>(const cCountedPtr<T>& rhs) : _counter(0), _ptr(0) { operator=(rhs); }

		virtual ~cCountedPtr<T>()
	   	{
            reset();
	   	}

		// assignment operator
		cCountedPtr<T>& operator=(const cCountedPtr<T>& rhs)
		{
			check_state(__LINE__);

			//printf("%s this %p n %d rhs %p n %d\n",__PRETTY_FUNCTION__,this,getCount(),&rhs,rhs.getCount());
			if(&rhs != this)
			{
				//printf("@@@@@@ %s this %p #1 T %p %u rhs %p T %p %u\n",__PRETTY_FUNCTION__,
				//		this,_ptr,getCount(),&rhs,rhs._ptr,rhs.getCount());
				if(_ptr != 0)
				{
					if(_counter == 0)
						throw "cCountedPtr<T> operator=() - _counter = 0";
					if(_ptr != rhs._ptr)
					{
						// this instance references a different object
						// delete that object before assignment
						//printf("%s this %p #1 T %p n %u\n",__PRETTY_FUNCTION__,this,_ptr,getCount());
						if(ATOMIC_DEC(_counter) == 0)
						{
							//printf("%s this %p #2\n",__PRETTY_FUNCTION__,this);
							delete _ptr;
							delete _counter;
						}
						// the new pointer could be null
						_ptr = rhs._ptr;
						_counter = rhs._counter;
						if(_counter != 0)
							ATOMIC_INC(_counter);
					}
				}
				else
				{
					//printf("%s this %p #3\n",__PRETTY_FUNCTION__,this);
					// this instance does not reference an object
					// the new reference could be null
					_ptr = rhs._ptr;
					_counter = rhs._counter;
					if(_counter != 0)
						ATOMIC_INC(_counter);
				}
				//printf("@@@@@@ %s this %p #2 T %p %u rhs %p T %p %u\n",__PRETTY_FUNCTION__,
				//		this,_ptr,getCount(),&rhs,rhs._ptr,rhs.getCount());
				//printf("%s this %p n %d T %p\n",__PRETTY_FUNCTION__,this,getCount(),_ptr);
			}
			return *this;
		}

		// comparison operator
		bool operator==(const cCountedPtr<T>& rhs)
		{
			return _ptr == rhs._ptr;
		}

		// conversion operators
		operator T* () const { return _ptr; }
		operator T& () const { return *_ptr; }

		// reference operators
		T* operator->() const { return _ptr; }
		T& operator* () const { return *_ptr; }
		T& operator[](const unsigned int i) const { return _ptr[i]; }
		T& operator[] (const int i) const { return _ptr[i]; }

		T* get() const { return _ptr; }
		unsigned int getCount() const
	   	{
			check_state(__LINE__);
		   	return _counter ? *_counter : 0;
	   	}
		bool isNull() const { return _ptr == 0; }
		bool notNull() const { return _ptr != 0; }

		// forget the pointer
		void reset()
		{
			check_state(__LINE__);
			if(_ptr != 0)
			{
				if(_counter == 0)
					throw "cCountedPtr<T>::reset() - _counter = 0";

				if(ATOMIC_DEC(_counter) == 0)
				{
					delete _ptr;
					delete _counter;
				}
				_ptr = 0;
				_counter = 0;
			}
		}

	private:
		unsigned int* _counter;
		T* _ptr;

		void check_state(const int line) const
		{
#if 0	/*disabled unused debugging to reduce overall code size*/
			// consistency check
			if(_ptr != 0 && _counter == 0)
				throw cExcept(__FILE__,line,"_ptr != 0 && _counter == 0");
			if(_ptr == 0 && _counter != 0)
				throw cExcept(__FILE__,line,"_ptr == 0 && _counter != 0");
#endif
		}

		// this assignment is not allowed
		// Keeping this method private forces me to be careful with assignments of objects
		// which for the most part are counted objects. (the compiler will flags these assignments)
		cCountedPtr<T>& operator=(const T* rhs);
};

#endif // _CPOINTER_H

