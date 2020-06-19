#@ String name
#@ int age
#@ String city
#@output Object greeting

from ij import IJ

greeting = "Hello " + name + ". You are " + age + " years old, and live in " + city + "."
IJ.log(greeting)