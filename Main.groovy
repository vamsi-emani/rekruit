package com.rekruit

import org.apache.tika.Tika

class Main {

    static main(args){
        try{
            def folder = '/Users/vamsie/Downloads/resumes'
            def inputs = "$folder/inputs"
            def baseDir = new File(folder)
            if(baseDir.exists()){
                new File(inputs).mkdir()
            }
            Tika tika = new Tika()
            baseDir.eachFileRecurse { file ->
                if(file.isFile()){
                    println "Parsing file $file"
                    def inputFileName = file.getName().substring(0, file.getName().lastIndexOf(".")) + '.txt'
                    def textFile = new File("$inputs/$inputFileName")
                    textFile.setText(tika.parseToString(file))
                }
            }
        }
        catch(e){
            e.printStackTrace()
        }

    }
}
