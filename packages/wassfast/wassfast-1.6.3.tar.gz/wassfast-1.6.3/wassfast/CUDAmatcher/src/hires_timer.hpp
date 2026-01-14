#ifndef HIRES_TIMER_H
#define HIRES_TIMER_H

#include <ostream>
#include <sstream>

#ifdef WIN32
#include <boost/chrono.hpp>
#endif

#if defined(UNIX) || defined(__linux__) || defined(__APPLE__)
#include <time.h>
#include <sys/time.h>
#endif




namespace cvlab {

template< typename TimerImpl >
class GenericHiresTimer
{
   public:

      inline GenericHiresTimer() : started(false), stopped(false), elapsed_time(0.0) {}
      inline ~GenericHiresTimer() {}

      inline void start( )
      {
          started = true; stopped = false;
          impl.start();
      }

      inline bool is_running() const { return (started==true && stopped==false); }

      inline double elapsed() const
      {
          if( started && !stopped )
              elapsed_time = impl.get_elapsed();

          return elapsed_time;
      }

      inline void stop()
      {
          elapsed(); // Update the elapsed_time cache
          stopped = true;
      }

      inline void reset()
      {
          started = stopped = false;
          elapsed_time = 0.0;
      }

      inline operator std::string() const
      {
          std::stringstream ss;
          ss << *this;
          return ss.str();
      }

   private:
      bool started;
      bool stopped;
      mutable double elapsed_time;
      TimerImpl impl;
};

template <typename T>
std::ostream& operator<<( std::ostream& os, GenericHiresTimer< T > timer )
{
    double el = timer.elapsed();
    size_t eli = static_cast<size_t>(el);

    if( eli>=60*60*24 )
    {
        os << (eli+1)/(60*60*24) << " days, ";
    }
    if( eli>=60*60 )
    {
        os << ((eli+1)/(60*60) % 24) << " hrs, ";
    }
    if( eli>=60 )
    {
        os << ((eli+1)/60 % 60) << " mins, ";
    }
    os << (eli%60)+(el-eli) << " secs.";

    return os;
}


#if defined(UNIX) || defined(__linux__) || defined(__APPLE__)
class UNIX_Timer_Impl
{
public:
    inline void start()
    {
        start_time = 0.0;
        start_time = get_elapsed();
    }

    inline double get_elapsed() const
    {
      struct timeval end_timeval;
      gettimeofday( &end_timeval, 0 );
      double tnow = (double)end_timeval.tv_sec + (double)end_timeval.tv_usec/1000000.0;
      return tnow-start_time;
    }

private:
      double start_time;
};

typedef GenericHiresTimer< UNIX_Timer_Impl > HiresTimer;
#endif

#ifdef WIN32
class WIN32_Timer_Impl
{
public:
    inline void start()
    {
		start_time = boost::chrono::high_resolution_clock::now();
    }

    inline double get_elapsed() const
    {
		return boost::chrono::duration_cast<boost::chrono::microseconds>(boost::chrono::high_resolution_clock::now() - start_time).count() * 1E-6;
    }

private:
	mutable boost::chrono::high_resolution_clock::time_point start_time;
};
typedef GenericHiresTimer< WIN32_Timer_Impl > HiresTimer;
#endif
}

#endif // HIRES_TIMER_H
