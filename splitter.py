from ffcuesplitter.cuesplitter import FFCueSplitter
from ffcuesplitter.user_service import FileSystemOperations
import shutil

def album_info(aCueSheet):
    respuesta = {}
    getdata = FFCueSplitter(filename=aCueSheet, dry=True)
    print("----------------------------------------------")
    if 'ALBUM' in getdata.cue.meta.data:
        print("Album: "+getdata.cue.meta.data['ALBUM'])
        respuesta['Album'] = getdata.cue.meta.data['ALBUM']
    if 'PERFORMER' in getdata.cue.meta.data:
        print("Intérpretes: "+getdata.cue.meta.data['PERFORMER'])
        respuesta['Interpretes'] = getdata.cue.meta.data['PERFORMER']
    if 'DATE' in getdata.cue.meta.data:
        print("Año: "+getdata.cue.meta.data['DATE'])
        respuesta['Fecha'] = getdata.cue.meta.data['DATE']
    if 'DISCID' in getdata.cue.meta.data:
        print("DISCID: "+getdata.cue.meta.data['DISCID'])
        respuesta['DISCID'] = getdata.cue.meta.data['DISCID']
    if 'CATALOG' in getdata.cue.meta.data:
        print("Nº Catálogo: "+getdata.cue.meta.data['CATALOG'])
        respuesta['catalog'] = getdata.cue.meta.data['CATALOG']
    print("*****************PISTAS***********************")
    indice = 0
    tracks = []
    for i in range(len(getdata.audiotracks)):
        if 'TITLE' in getdata.audiotracks[i]:
            print(getdata.audiotracks[i]['TITLE'])
            tracks.append(getdata.audiotracks[i]['TITLE'])
    print("----------------------------------------------")
    respuesta['tracks'] = tracks
    return respuesta

#TODO: Se puede intentar que se puedan seleccionar más parámetros
def split_it_like_solomon(cue):
    split = FileSystemOperations(
        filename=cue, 
        outputdir=cue.split('.')[0],
        ffmpeg_loglevel='verbose',
        overwrite='always'
    )
    if split.kwargs["dry"]:
        split.dry_run_mode()
    else:
        overwr = split.check_for_overwriting()
        if not overwr:
            split.work_on_temporary_directory()

    return shutil.make_archive(cue.split('.')[0],'zip',cue.split('.')[0])