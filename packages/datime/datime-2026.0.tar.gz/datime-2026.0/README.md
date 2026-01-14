# datime

Python package with convenience functions for dates, times, and intervals

## Usage

### `pretty_duration_short`

Use the function `pretty_duration_short` to convert a whole number of seconds to a string that indicates the number of
hours, minutes, and seconds in the provided duration.

```pycon
>>> import datime
>>> datime.pretty_duration_short(59)
'59s'
>>> datime.pretty_duration_short(256)
'4m16s'
>>> datime.pretty_duration_short(60 * 60)
'1h0m0s'
>>> datime.pretty_duration_short(4096)
'1h8m16s'
>>> datime.pretty_duration_short(2**17)
'36h24m32s'
```
