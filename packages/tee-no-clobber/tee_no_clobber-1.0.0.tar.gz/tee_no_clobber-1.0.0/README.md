# tee-no-clobber
A version of the tee command line utility which does not write over files that exist

## Alternatives and motivation
Shells can have no clobber options. But I prefer the power of clobbering files, untl I don't want it.

## Installation
pipx install tee-no-clobbler

## Usage
Write to hello into file if it does not exist.

echo hello | teenc file
