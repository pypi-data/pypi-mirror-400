# Configuration


## About
Tool to retrieve configuration data, either for .ENV or .ini files

## get started
- provide configuration data using:
  - .ENV: FOO_BAR = hello 
  - .ini: located in same dir as executing script, can be from multiple files
  [foo]
  bar = hello

- retrieve: 
    - MyConfig('foo').get('bar')
    - MyConfig('foo', ['bar']).bar







