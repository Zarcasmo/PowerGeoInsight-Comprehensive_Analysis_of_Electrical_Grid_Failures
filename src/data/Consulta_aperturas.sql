select t4.* from(
select cod_elemento,ide_evento,ide_maniobra_desenergizacion as maniobra,IDE_CODIGO_CLASE,CODIGO,NOM_CODIGO,anio, mes, dia, max(dur_h) as dur_h, sum(prom_h) as prom_h, sum(num_aperturas) as num_aperturas from
(select t2.*, t3.cod_elemento from (
select ide_evento,ide_maniobra_desenergizacion,IDE_CODIGO_CLASE, CODIGO, NOM_CODIGO, anio, mes, dia, max(dur_h) as dur_h, trunc(avg(dur_h),3) as prom_h, count(distinct ide_maniobra_desenergizacion) as num_aperturas from(
SELECT 
    ta.ide_evento,
    ta.ide_maniobra_desenergizacion,   
    round(extract(day from (ta.fec_energizacion -ta.fec_desenergizacion))*24
    +(extract(hour from (ta.fec_energizacion -ta.fec_desenergizacion))
    + extract(minute from (ta.fec_energizacion -ta.fec_desenergizacion))/60
    + extract(second from (ta.fec_energizacion -ta.fec_desenergizacion))/3600),3) as dur_h,
    extract(year from (ta.fec_desenergizacion)) as anio,
    extract(month from (ta.fec_desenergizacion)) as mes,
    extract(day from (ta.fec_desenergizacion)) as dia,
    ta.ide_codigo_apertura CODIGO,
    tb.nom_codigo_apertura NOM_CODIGO,
    tc.IDE_CODIGO_CLASE
FROM DMS.dmst_trafo_afectado ta, dms.dmst_codigo_apertura tb, dms.dmst_cal_clase_apertura tc
WHERE 
ta.ide_codigo_apertura=tb.ide_codigo_apertura and
tb.ide_clase_apertura_015=tc.ide_clase_apertura and
ta.fec_desenergizacion >= TO_DATE(:fecha_inicio,'yyyy-mm-dd') and ta.fec_desenergizacion < TO_DATE(:fecha_fin,'yyyy-mm-dd')
and tc.tipo_regulacion ='CREG 015'
and tc.IDE_CODIGO_CLASE not in ('Eventos de Activos del STN y el STR','Racionamiento de Emergencia por Eventos de Generación','Acuerdos de Calidad en las Zonas Especiales')
) t1 GROUP by ide_evento, ide_maniobra_desenergizacion,IDE_CODIGO_CLASE,CODIGO,NOM_CODIGO, anio, mes, dia) t2 join 
(select ide_maniobra, cod_elemento from DMS.dmst_maniobra) t3 on t2.ide_maniobra_desenergizacion=t3.ide_maniobra) 
GROUP BY cod_elemento,ide_evento,ide_maniobra_desenergizacion,IDE_CODIGO_CLASE,CODIGO,NOM_CODIGO,anio, mes, dia) t4 join (select cod_elemento, tip_elemento from DMS.dmst_red_elemento) t5 on t4.cod_elemento = t5.cod_elemento where t5.tip_elemento in (405,408,404,409) and t4.cod_elemento not like 'SW%'