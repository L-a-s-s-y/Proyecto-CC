from ffcuesplitter.cuesplitter import FFCueSplitter
from ffcuesplitter.user_service import FileSystemOperations
import shutil
import psycopg2

def crear_tabla(conexion, el_cursor):
    el_cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)",("chopped_musical",))
    if not el_cursor.fetchone()[0]:
        el_cursor.execute("""
            CREATE TABLE chopped_musical(
                discid      char(8) CONSTRAINT discid PRIMARY KEY,
                title       varchar(150),
                performer   varchar(150),
                date        smallint,
                genre       varchar(100)
            );
        """)
    conexion.commit()

def album_info(aCueSheet):
    conexion = psycopg2.connect(
        dbname="music_chops",
        user="postgres",
        password="1234",
        host="localhost"
        #host="my-postgres-database"
    )
    el_cursor = conexion.cursor()
    crear_tabla(conexion, el_cursor)
    respuesta = {}
    getdata = FFCueSplitter(filename=aCueSheet, dry=True)
    do_not_repeat = False
    el_cursor.execute("SELECT discid FROM public.chopped_musical WHERE discid = %s",(getdata.cue.meta.data['DISCID'],))
    do_not_repeat = el_cursor.fetchone() is None
    print("----------------------------------------------")
    if 'DISCID' in getdata.cue.meta.data:
        print("DISCID: "+getdata.cue.meta.data['DISCID'])
        respuesta['DISCID'] = getdata.cue.meta.data['DISCID']
        if do_not_repeat:
            el_cursor.execute("INSERT INTO public.chopped_musical (discid, title, performer, date, genre) VALUES (%s,%s,%s,%s,%s)", (respuesta['DISCID'], 'XXYYYYZZ', 'XXYYYYZZ', '1999', 'XXYYYYZZ'))

    if 'ALBUM' in getdata.cue.meta.data:
        print("Album: "+getdata.cue.meta.data['ALBUM'])
        respuesta['Album'] = getdata.cue.meta.data['ALBUM']
        if do_not_repeat:
            el_cursor.execute("UPDATE public.chopped_musical SET title = %s WHERE discid = %s",(respuesta['Album'],respuesta['DISCID']))

    if 'PERFORMER' in getdata.cue.meta.data:
        print("Intérpretes: "+getdata.cue.meta.data['PERFORMER'])
        respuesta['Interpretes'] = getdata.cue.meta.data['PERFORMER']
        if do_not_repeat:
            el_cursor.execute("UPDATE public.chopped_musical SET performer = %s WHERE discid = %s",(respuesta['Interpretes'],respuesta['DISCID']))

    if 'DATE' in getdata.cue.meta.data:
        print("Año: "+getdata.cue.meta.data['DATE'])
        respuesta['Fecha'] = getdata.cue.meta.data['DATE']
        if do_not_repeat:
            el_cursor.execute("UPDATE public.chopped_musical SET date = %s WHERE discid = %s",(respuesta['Fecha'],respuesta['DISCID']))

    if 'CATALOG' in getdata.cue.meta.data:
        print("Nº Catálogo: "+getdata.cue.meta.data['CATALOG'])
        respuesta['catalog'] = getdata.cue.meta.data['CATALOG']

    if 'GENRE' in getdata.cue.meta.data:
        print("Género: "+getdata.cue.meta.data['GENRE'])
        respuesta['Genero'] = getdata.cue.meta.data['GENRE']
        if do_not_repeat:
            el_cursor.execute("UPDATE public.chopped_musical SET genre = %s WHERE discid = %s",(respuesta['Genero'],respuesta['DISCID']))


    print("*****************PISTAS***********************")
    indice = 0
    tracks = []
    for i in range(len(getdata.audiotracks)):
        if 'TITLE' in getdata.audiotracks[i]:
            print(getdata.audiotracks[i]['TITLE'])
            tracks.append(getdata.audiotracks[i]['TITLE'])
    print("----------------------------------------------")
    respuesta['tracks'] = tracks
    conexion.commit()
    el_cursor.close()
    conexion.close()
    return respuesta

#TODO: Se puede intentar que se puedan seleccionar más parámetros
def split_it_like_solomon(cue):
    split = FileSystemOperations(
        filename=cue,
        outputdir=cue.split('.')[0],
        #outputformat="copy",
        progress_meter='tqdm',
        prg_loglevel='info',
        ffmpeg_loglevel='error',
        overwrite='always'
    )
    if split.kwargs["dry"]:
        split.dry_run_mode()
    else:
        overwr = split.check_for_overwriting()
        if not overwr:
            split.work_on_temporary_directory()

    return shutil.make_archive(cue.split('.')[0],'zip',cue.split('.')[0])