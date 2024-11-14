from ffcuesplitter.cuesplitter import FFCueSplitter
from ffcuesplitter.user_service import FileSystemOperations


def splittingFunc(directorio):
    directorio="CUEs/"+directorio
    split = FileSystemOperations(filename="CUEs/Schumann - Test - FLAC.cue", outputdir=directorio)
    if split.kwargs["dry"]:
        split.dry_run_mode()
    else:
        overwr = split.check_for_overwriting()
        if not overwr:
            split.work_on_temporary_directory()

# Función como prueba de las distintas fuciones de la clase FFCueSplitter
def funcTestFunc(aCueSheet):
    getdata = FFCueSplitter(filename=aCueSheet, dry=True)
    # getdata = FFCueSplitter(filename="CUEs/Schumann - Test - FLAC.cue", dry=True)
    # getdata = FFCueSplitter(filename="CUEs/Three Samples_ASCII.cue", dry=True)
    # result = getdata.check_cuefile()
    # print("check_cuefile: " + str(result))
    # result = getdata.deflacue_object_handler()
    # print("deflacue_object_handler: "+result)
    print(getdata.cue.meta.data)
    print("----------------------------------------------")
    # print(getdata.audiotracks)
    # print("----------------------------------------------")
    # print(getdata.cue_encoding)
    # print("----------------------------------------------")
    #splittingFunc()
    print(type(getdata.cue.meta.data))
    print("----------------------------------------------")
    #splittingFunc(getdata.cue.meta.data["ALBUM"])
    return type(getdata.cue.meta.data)


if __name__ == '__main__':
    funcTestFunc("CUEs/Schumann - Test - FLAC.cue")
    #splittingFunc()

