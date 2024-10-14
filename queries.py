from datetime import datetime

class Queries:
    def __init__(self, start_date, end_date):
        # Convert dates from 'yyyy-mm-dd' to 'yyyymmdd'
        start_date_str = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        end_date_str = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')

        self.vas1 = f"""
WITH FilteredVAS AS (
    SELECT 
        VASCRE || VAACRE || LPAD(VAMCRE, 2, 0) || LPAD(VAJCRE, 2, 0) AS CREATION_DATE,
        SUM(A.Expoloded) AS TOTAL_EXPLODED
    FROM GUEPRD_dat.gnvacop 
    LEFT JOIN (
        SELECT DISTINCT EVCVAS CODE, EVLVAS FROM GUEPRD_dat.GNSDEVP
    ) C ON C.CODE = VAVCOD
    INNER JOIN (
        SELECT 
            SUM(A.SUM) AS QTY, 
            SUM(A.SUM * A.LOTTO) AS Expoloded, 
            LPAD(A.gensup, 18, 0) AS HD1
        FROM (
            SELECT 
                SUM(geqgei) AS SUM, 
                gecart, 
                gensup, 
                CASE WHEN LOT.SUM1 IS NULL THEN '1' ELSE LOT.SUM1 END AS LOTTO, 
                AITLOT,  
                gecdpo    
            FROM GUEPRDDB.hlgeinp                                                        
            LEFT OUTER JOIN GUEPRD_DAT.GNARCAP ON geCART = AICART                    
            LEFT OUTER JOIN (
                SELECT CTCACT, CTCART, SUM(CTQCOM) AS SUM1 
                FROM GUEPRDDB.HLCOMPP 
                GROUP BY CTCACT, CTCART
            ) LOT ON geCART = CTCART               
            WHERE GECTST = '200' 
            GROUP BY gecart, gecdpo, CASE WHEN LOT.SUM1 IS NULL THEN '1' ELSE LOT.SUM1 END, AITLOT, gensup
            UNION 
            SELECT 
                SUM(GSQGEI) AS SUM, 
                gscart, 
                GSNSUP, 
                CASE WHEN LOT.SUM1 IS NULL THEN '1' ELSE LOT.SUM1 END AS LOTTO, 
                AITLOT,  
                gscdpo 
            FROM GUEPRDDB.hlgesop                                                        
            LEFT OUTER JOIN GUEPRD_DAT.GNARCAP ON gsCART = AICART                    
            LEFT OUTER JOIN (
                SELECT CTCACT, CTCART, SUM(CTQCOM) AS SUM1 
                FROM GUEPRDDB.HLCOMPP 
                GROUP BY CTCACT, CTCART
            ) LOT ON gsCART = CTCART               
            WHERE GsCTST = '200' 
            GROUP BY gscart, gscdpo, CASE WHEN LOT.SUM1 IS NULL THEN '1' ELSE LOT.SUM1 END, AITLOT, gsnsup
        ) A  
        GROUP BY LPAD(A.gensup, 18, 0)
    ) A ON A.HD1 = vancol 
    LEFT JOIN (
        SELECT DISTINCT 
            LPAD(gensup, 18, 0) AS HD, 
            OWRODP AS Prebola 
        FROM GUEPRDDB.hlgeinp 
        INNER JOIN GUEPRDDB.HLLPRGL2 ON LGNGEI = gengei
        INNER JOIN GUEPRDDB.HLPRPLL1 ON LGNANN = P1NANN AND LGNLPR = P1NLPR
        INNER JOIN gueprd_dat.GNODWAP ON OWNAPR = P1NANP AND P1NPRE = OWNPRE
        UNION
        SELECT DISTINCT 
            LPAD(GSNSUP, 18, 0) AS HD, 
            GSRODP AS Prebola 
        FROM GUEPRDDB.hlgesop
    ) PREBOLA ON PREBOLA.HD = vancol
    INNER JOIN gueprd_dat.gnordop ON PREBOLA.Prebola = gordor
    INNER JOIN Gueprd_dat.gnopvgp ON OPRODP = gordor
    LEFT OUTER JOIN (
        SELECT DISTINCT 
            SUCTSU AS tipo, 
            LPAD(sunsup, 18, 0) AS HD2 
        FROM GUEPRDDB.hlsuppp 
        UNION
        SELECT DISTINCT 
            GSCTSU AS tipo, 
            LPAD(GSNSUP, 18, 0) AS HD2 
        FROM GUEPRDDB.HLGESOL4
    ) T ON T.HD2 = vancol
    WHERE 
        VASMAJ || VAAMAJ || LPAD(VAMMAJ, 2, 0) || LPAD(VAJMAJ, 2, 0) BETWEEN 
        {start_date_str} AND {end_date_str} 
        AND VAFDON = '1'
        AND TRIM(OPGVA1) NOT IN ('70')
        AND TRIM(C.EVLVAS) NOT IN (
            'MAX VOL 0,072', 
            'MAX VOL 0,096', 
            'MAX WEIGHT 15 KG', 
            'PACK GOH AND FLAT TOGETHER', 
            'PACK GOH FOLDED, KEEP HANGERS', 
            'PACK GOH FOLDED, REMOVE HANGERS', 
            'Print 2 plist out of the carton', 
            'DATAMATRIX LABELLING'
        )
    GROUP BY 
        VASCRE || VAACRE || LPAD(VAMCRE, 2, 0) || LPAD(VAJCRE, 2, 0)
)
SELECT 
    CREATION_DATE, 
    SUM(TOTAL_EXPLODED) AS TOTAL_EXPLODED
FROM FilteredVAS
GROUP BY CREATION_DATE
ORDER BY CREATION_DATE"""

        self.vas =f"""WITH MainQuery AS (
    SELECT 
        PREBOLA.Prebola AS PREBOLA,
        GOCCHE AS INSTRUMENT,
        GOCFAM AS LINE,
        OPFL07 AS FLAG_7,
        OPGVA1 AS HANDLING_GROUP,
        LPAD(VANCOL, 18, 0) AS HD,
        T.tipo AS CARTON_TYPE,
        A.QTY AS QTY,
        A.Expoloded AS EXPLODED,
        VAVCOD AS VAS_CODE,
        C.EVLVAS AS VAS,
        VAFDON AS VAS_DONE,
        VASCRE || VAACRE || LPAD(VAMCRE, 2, 0) || LPAD(VAJCRE, 2, 0) AS CREATION_DATE,
        LPAD(VAHCRE, 6, 0) AS CREATION_HOUR,
        VAUCRE AS CREATION_USER,
        VASMAJ || VAAMAJ || LPAD(VAMMAJ, 2, 0) || LPAD(VAJMAJ, 2, 0) AS UPDATE_DATE,
        LPAD(VAHMAJ, 6, 0) AS UPDATE_HOUR,
        VAUMAJ AS UPDATE_USER
    FROM GUEPRD_dat.gnvacop
    LEFT JOIN (SELECT DISTINCT EVCVAS AS CODE, EVLVAS FROM GUEPRD_dat.GNSDEVP) C ON C.CODE = VAVCOD
    INNER JOIN (
        SELECT 
            SUM(A.SUM) AS QTY, 
            SUM(A.SUM * A.LOTTO) AS Expoloded, 
            LPAD(A.gensup, 18, 0) AS HD1
        FROM (
            SELECT 
                SUM(geqgei) AS SUM,
                gecart,
                gensup,
                COALESCE(LOT.SUM1, '1') AS LOTTO,
                AITLOT,
                gecdpo
            FROM GUEPRDDB.hlgeinp
            LEFT OUTER JOIN GUEPRD_DAT.GNARCAP ON geCART = AICART
            LEFT OUTER JOIN (
                SELECT CTCACT, CTCART, SUM(CTQCOM) AS SUM1
                FROM GUEPRDDB.HLCOMPP
                GROUP BY CTCACT, CTCART
            ) LOT ON geCART = CTCART
            WHERE GECTST = '200'
            GROUP BY gecart, gecdpo, COALESCE(LOT.SUM1, '1'), AITLOT, gensup
        ) A
        GROUP BY LPAD(A.gensup, 18, 0)
        UNION
        SELECT 
            SUM(A.SUM) AS QTY,
            SUM(A.SUM * A.LOTTO) AS Expoloded,
            LPAD(A.GSNSUP, 18, 0) AS HD1
        FROM (
            SELECT 
                SUM(GSQGEI) AS SUM,
                gscart,
                GSNSUP,
                COALESCE(LOT.SUM1, '1') AS LOTTO,
                AITLOT,
                gscdpo
            FROM GUEPRDDB.hlgesop
            LEFT OUTER JOIN GUEPRD_DAT.GNARCAP ON gsCART = AICART
            LEFT OUTER JOIN (
                SELECT CTCACT, CTCART, SUM(CTQCOM) AS SUM1
                FROM GUEPRDDB.HLCOMPP
                GROUP BY CTCACT, CTCART
            ) LOT ON gsCART = CTCART
            WHERE GsCTST = '200'
            GROUP BY gscart, gscdpo, COALESCE(LOT.SUM1, '1'), AITLOT, gsnsup
        ) A
        GROUP BY LPAD(A.gsnsup, 18, 0)
    ) A ON A.HD1 = VANCOL
    LEFT JOIN (
        SELECT DISTINCT LPAD(gensup, 18, 0) AS HD, OWRODP AS Prebola
        FROM GUEPRDDB.hlgeinp
        INNER JOIN GUEPRDDB.HLLPRGL2 ON LGNGEI = gengei
        INNER JOIN GUEPRDDB.HLPRPLL1 ON LGNANN = P1NANN AND LGNLPR = P1NLPR
        INNER JOIN gueprd_dat.GNODWAP ON OWNAPR = P1NANP AND P1NPRE = OWNPRE
        UNION
        SELECT DISTINCT LPAD(GSNSUP, 18, 0) AS HD, GSRODP AS Prebola
        FROM GUEPRDDB.hlgesop
    ) PREBOLA ON PREBOLA.HD = VANCOL
    INNER JOIN gueprd_dat.gnordop ON PREBOLA.Prebola = gordor
    INNER JOIN Gueprd_dat.gnopvgp ON OPRODP = gordor
    LEFT OUTER JOIN (
        SELECT DISTINCT SUCTSU AS tipo, LPAD(sunsup, 18, 0) AS HD2
        FROM GUEPRDDB.hlsuppp
        UNION
        SELECT DISTINCT GSCTSU AS tipo, LPAD(GSNSUP, 18, 0) AS HD2
        FROM GUEPRDDB.HLGESOL4
    ) T ON T.HD2 = VANCOL
    WHERE VASMAJ || VAAMAJ || LPAD(VAMMAJ, 2, 0) || LPAD(VAJMAJ, 2, 0) BETWEEN
        {start_date_str} AND {end_date_str} 
    AND VAFDON = '1'
)
SELECT
    UPDATE_DATE,
    SUM(EXPLODED) AS TOTAL_EXPLODED
FROM MainQuery
WHERE TRIM(HANDLING_GROUP) <> '70' AND (SUBSTRING(VAS_CODE, 1, 2) = '15' or VAS_CODE in ( '063','141','144','145','147','148','14A', 'CON'))
  AND TRIM(VAS) NOT IN (
    'MAX VOL 0,072', 
    'MAX VOL 0,096', 
    'MAX WEIGHT 15 KG', 
    'PACK GOH AND FLAT TOGETHER', 
    'PACK GOH FOLDED, KEEP HANGERS', 
    'PACK GOH FOLDED, REMOVE HANGERS', 
    'Print 2 plist out of the carton', 
    'DATAMATRIX LABELLING',
    'only W3 allowed',
    'MONO SKU PACKAGING',
    'max carton weight 13 kg'
  )  -- Moved this filter here
GROUP BY UPDATE_DATE
ORDER BY UPDATE_DATE"""
        
#AND (SUBSTRING(VAS_CODE, 1, 2) = '15' or VAS_CODE in ( '063','141','144','145','147','148','14A', 'CON'))