# rekruit - IT Resume screener. 

### Main.groovy 
Resume files in various formats such as (.pdf, .doc) under a given input directory are converted into text files and the output directory containining resume files in `.txt` format is passed as input to the python script.

### script.py
Uses regex and nltk library functions in tandem with known keywords to eliminate noise 
and mine useful information from the resume that the employers would be interested in. 

Details extracted from resume 

- Useful links to git repos, personal tech blogs, stackoverflow QnAs et al if mentioned
- Email and contact number
- Education 
- Ceritifications and experience
- Experience

### TODO
The output (Resume) of this python script can further be enhanced via an algorithm that 
can rank resumes on a scale of 1-5.

