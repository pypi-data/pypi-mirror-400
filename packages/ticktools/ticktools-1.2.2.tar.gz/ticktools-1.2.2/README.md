# ChronoKit

A stopwatch/timer utillity

## Installation

```bash
pip install ticktools
```

## Importing

```python
from chronokit import *
```

## Usage

### stopwatch
#### start()
The function start() in the class stopwatch takes no arguments. It starts the stopwatch.
```python
stopwatch.start()
```
#### stop()
The function stop() in the class stopwatch takes no arguments. It stops the stopwatch.
```python
stopwatch.stop()
```
#### resume()
The function resume() in the class stopwatch takes no arguments. It resumes the timer once it was stopped.
```python
stopwatch.resume()
```
#### lap()
The function lap() in the class stopwatch takes no arguments. It makes a lap.
```python
stopwatch.lap()
```
#### returntime()
The function returntime() in the class stopwatch takes no arguments. It returns the time the stopwatch has run.
```python
time = stopwatch.returntime()
```
#### returnlaps()
The function returnlaps() in the class stopwatch takes no arguments. It returns the laps in list format.
```python
laps = stopwatch.returnlaps()
```
#### reset()
The function reset() in the class stopwatch takes no arguments. It resets the stopwatch.
```python
stopwatch.start()
wait(2000)
stopwatch.reset() #Works even when stopwatch is running
wait(1000)
stopwatch.stop()
stopwatch.reset() #Also works when stopwatch has been stopped
```
### wait()

The function wait() takes one argument: the amout of time to wait in milliseconds.

```python
wait(1000)
```

### from_start()

The function from_start() doesn't take any arguments. When you call the function, it returns the time elapsed since the module was imported

```python
from_start()
```

### deadline()
The function deadline takes two arguments: The amount of time it should run in milliseconds and the function it should run.

```python
deadline(3000, lambda elapsed: print(elapsed)) #The function MUST have an argument called 'elapsed'
```