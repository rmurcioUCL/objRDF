__author__ = '3cixty team'

from RDFclass import RDFclass

# define main function interface
if __name__ == "__main__":

    # csv filename
    inputfile="bus-stops-10-06-15.csv";

    # RDF filename
    outputfile="test.ttl";

    f=RDFclass()

    csv=f.readCsv(inputfile)

    if csv is not None:
        # Skip the headers
        next(csv, None)
        for row in csv:
            # for python 3.4 users
            print(row)

            # for python 2.7 users
            #print row

            f.creatRDF(row)
            #break;

        f.writeRDF(outputfile)

    # for python 3.4 users
    print("csv file has been converted to RDF turtle successfully !")

    # for python 2.7 users
    #print "csv file has been converted to RDF turtle successfully !"
