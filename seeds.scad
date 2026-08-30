// SeedPills: 3D-printable BIP39 word pills.
//
// Defaults are tuned for a 0.4mm nozzle (Bambu P1S) at 0.2mm layers, with
// every small feature an integer number of extrusion lines or layers:
//   - total height   2.60mm = 13 x 0.2mm layers
//   - base height    1.60mm =  8 x 0.2mm layers
//   - raised text    1.00mm =  5 x 0.2mm layers
//   - standalone pills have a 0.40mm separation (one nozzle width)
//
// Single-sided by default: one word per pill, printed flat with no flip.
// A full 2048-word set is 2048 pills (8 plates at 13x22 on a 256mm bed,
// leaving a lower band for the plate ID and prime tower).

$fa = 6;    // smooth pill ends
$fs = 0.8;  // curve resolution; smooth at this radius. The mesh is large but
            // exported as 3MF (compressed), so the slicer stays responsive

// Grid
first = 0;         // index of the first word in this grid (0 = "ABAN")
columns = 13;      // pills per row; 0 = auto from bed
rows = 22;         // pills per column; 0 = auto from bed
bed = [256, 256];    // build plate size (P1S/X1C = 256x256), used when
                     // columns/rows are 0
bed_margin = 4;        // keep-out per side, room for skirt/brim
exclusion = [18, 28];  // P1S/X1 front-left corner reserved for the filament
                       // cutter + wiper; the grid is shifted clear of it
prime_tower = [20, 20]; // requested tower footprint; its width is reserved as
                        // a clear strip along the right edge of the plate
show_plate_id = true;   // add a standalone P1/7-style plate marker
plate_number = 1;       // set automatically by render_batches.py
plate_count = 8;
plate_id_size = [18, 10];

// Pill
width = 18.5;   // overall pill length
lenght = 7.5;   // overall pill width
height = 1.6;      // flat pill base: 8 layers at 0.2mm
text_height = 1.0; // raised lettering: 5 layers; 2.6mm total height

// Lettering
double_sided = false;  // true = word i+1024 on the back face (halves the
                       // pill count but requires flipping / two-sided print)
font = "PT Mono:style=Bold"; // compact monospace keeps codes distinct
font_size = 4.2;             // source size before geometry-aware fitting
text_weight = 0.12;          // outward offset fattens each glyph stroke
text_box_width = [13.0, 15.2]; // fitted widths for 3- and 4-letter labels
text_box_height = 4.6;         // fitted height; clears the rounded pill ends

// Multi-color export
render_part = "both";        // "both", "base", or "text"
base_color = "#202020";     // filament 1: black base
text_color = "#F97316";     // filament 2: orange raised text

// Documentation-preview helpers. Leave false for printable exports.
show_build_plate = false;
show_prime_tower = false;

// Spacing / interlocks
connected = false;        // true adds breakaway links to keep a plate ordered
spacing = 0.4;            // one nozzle width: close without touching in CAD
interlock = 0.5;          // one extrusion line: printable but snaps by hand
interlock_overlap = 0.04; // embed into each pill for a clean boolean union

words = ["ABAN","ABIL","ABLE","ABOU","ABOV","ABSE","ABSO","ABST","ABSU","ABUS","ACCE","ACCI","ACCO","ACCU","ACHI","ACID","ACOU","ACQU","ACRO","ACT","ACTI","ACTO","ACTR","ACTU","ADAP","ADD","ADDI","ADDR","ADJU","ADMI","ADUL","ADVA","ADVI","AERO","AFFA","AFFO","AFRA","AGAI","AGE","AGEN","AGRE","AHEA","AIM","AIR","AIRP","AISL","ALAR","ALBU","ALCO","ALER","ALIE","ALL","ALLE","ALLO","ALMO","ALON","ALPH","ALRE","ALSO","ALTE","ALWA","AMAT","AMAZ","AMON","AMOU","AMUS","ANAL","ANCH","ANCI","ANGE","ANGL","ANGR","ANIM","ANKL","ANNO","ANNU","ANOT","ANSW","ANTE","ANTI","ANXI","ANY","APAR","APOL","APPE","APPL","APPR","APRI","ARCH","ARCT","AREA","AREN","ARGU","ARM","ARME","ARMO","ARMY","AROU","ARRA","ARRE","ARRI","ARRO","ART","ARTE","ARTI","ARTW","ASK","ASPE","ASSA","ASSE","ASSI","ASSU","ASTH","ATHL","ATOM","ATTA","ATTE","ATTI","ATTR","AUCT","AUDI","AUGU","AUNT","AUTH","AUTO","AUTU","AVER","AVOC","AVOI","AWAK","AWAR","AWAY","AWES","AWFU","AWKW","AXIS","BABY","BACH","BACO","BADG","BAG","BALA","BALC","BALL","BAMB","BANA","BANN","BAR","BARE","BARG","BARR","BASE","BASI","BASK","BATT","BEAC","BEAN","BEAU","BECA","BECO","BEEF","BEFO","BEGI","BEHA","BEHI","BELI","BELO","BELT","BENC","BENE","BEST","BETR","BETT","BETW","BEYO","BICY","BID","BIKE","BIND","BIOL","BIRD","BIRT","BITT","BLAC","BLAD","BLAM","BLAN","BLAS","BLEA","BLES","BLIN","BLOO","BLOS","BLOU","BLUE","BLUR","BLUS","BOAR","BOAT","BODY","BOIL","BOMB","BONE","BONU","BOOK","BOOS","BORD","BORI","BORR","BOSS","BOTT","BOUN","BOX","BOY","BRAC","BRAI","BRAN","BRAS","BRAV","BREA","BREE","BRIC","BRID","BRIE","BRIG","BRIN","BRIS","BROC","BROK","BRON","BROO","BROT","BROW","BRUS","BUBB","BUDD","BUDG","BUFF","BUIL","BULB","BULK","BULL","BUND","BUNK","BURD","BURG","BURS","BUS","BUSI","BUSY","BUTT","BUYE","BUZZ","CABB","CABI","CABL","CACT","CAGE","CAKE","CALL","CALM","CAME","CAMP","CAN","CANA","CANC","CAND","CANN","CANO","CANV","CANY","CAPA","CAPI","CAPT","CAR","CARB","CARD","CARG","CARP","CARR","CART","CASE","CASH","CASI","CAST","CASU","CAT","CATA","CATC","CATE","CATT","CAUG","CAUS","CAUT","CAVE","CEIL","CELE","CEME","CENS","CENT","CERE","CERT","CHAI","CHAL","CHAM","CHAN","CHAO","CHAP","CHAR","CHAS","CHAT","CHEA","CHEC","CHEE","CHEF","CHER","CHES","CHIC","CHIE","CHIL","CHIM","CHOI","CHOO","CHRO","CHUC","CHUN","CHUR","CIGA","CINN","CIRC","CITI","CITY","CIVI","CLAI","CLAP","CLAR","CLAW","CLAY","CLEA","CLER","CLEV","CLIC","CLIE","CLIF","CLIM","CLIN","CLIP","CLOC","CLOG","CLOS","CLOT","CLOU","CLOW","CLUB","CLUM","CLUS","CLUT","COAC","COAS","COCO","CODE","COFF","COIL","COIN","COLL","COLO","COLU","COMB","COME","COMF","COMI","COMM","COMP","CONC","COND","CONF","CONG","CONN","CONS","CONT","CONV","COOK","COOL","COPP","COPY","CORA","CORE","CORN","CORR","COST","COTT","COUC","COUN","COUP","COUR","COUS","COVE","COYO","CRAC","CRAD","CRAF","CRAM","CRAN","CRAS","CRAT","CRAW","CRAZ","CREA","CRED","CREE","CREW","CRIC","CRIM","CRIS","CRIT","CROP","CROS","CROU","CROW","CRUC","CRUE","CRUI","CRUM","CRUN","CRUS","CRY","CRYS","CUBE","CULT","CUP","CUPB","CURI","CURR","CURT","CURV","CUSH","CUST","CUTE","CYCL","DAD","DAMA","DAMP","DANC","DANG","DARI","DASH","DAUG","DAWN","DAY","DEAL","DEBA","DEBR","DECA","DECE","DECI","DECL","DECO","DECR","DEER","DEFE","DEFI","DEFY","DEGR","DELA","DELI","DEMA","DEMI","DENI","DENT","DENY","DEPA","DEPE","DEPO","DEPT","DEPU","DERI","DESC","DESE","DESI","DESK","DESP","DEST","DETA","DETE","DEVE","DEVI","DEVO","DIAG","DIAL","DIAM","DIAR","DICE","DIES","DIET","DIFF","DIGI","DIGN","DILE","DINN","DINO","DIRE","DIRT","DISA","DISC","DISE","DISH","DISM","DISO","DISP","DIST","DIVE","DIVI","DIVO","DIZZ","DOCT","DOCU","DOG","DOLL","DOLP","DOMA","DONA","DONK","DONO","DOOR","DOSE","DOUB","DOVE","DRAF","DRAG","DRAM","DRAS","DRAW","DREA","DRES","DRIF","DRIL","DRIN","DRIP","DRIV","DROP","DRUM","DRY","DUCK","DUMB","DUNE","DURI","DUST","DUTC","DUTY","DWAR","DYNA","EAGE","EAGL","EARL","EARN","EART","EASI","EAST","EASY","ECHO","ECOL","ECON","EDGE","EDIT","EDUC","EFFO","EGG","EIGH","EITH","ELBO","ELDE","ELEC","ELEG","ELEM","ELEP","ELEV","ELIT","ELSE","EMBA","EMBO","EMBR","EMER","EMOT","EMPL","EMPO","EMPT","ENAB","ENAC","END","ENDL","ENDO","ENEM","ENER","ENFO","ENGA","ENGI","ENHA","ENJO","ENLI","ENOU","ENRI","ENRO","ENSU","ENTE","ENTI","ENTR","ENVE","EPIS","EQUA","EQUI","ERA","ERAS","EROD","EROS","ERRO","ERUP","ESCA","ESSA","ESSE","ESTA","ETER","ETHI","EVID","EVIL","EVOK","EVOL","EXAC","EXAM","EXCE","EXCH","EXCI","EXCL","EXCU","EXEC","EXER","EXHA","EXHI","EXIL","EXIS","EXIT","EXOT","EXPA","EXPE","EXPI","EXPL","EXPO","EXPR","EXTE","EXTR","EYE","EYEB","FABR","FACE","FACU","FADE","FAIN","FAIT","FALL","FALS","FAME","FAMI","FAMO","FAN","FANC","FANT","FARM","FASH","FAT","FATA","FATH","FATI","FAUL","FAVO","FEAT","FEBR","FEDE","FEE","FEED","FEEL","FEMA","FENC","FEST","FETC","FEVE","FEW","FIBE","FICT","FIEL","FIGU","FILE","FILM","FILT","FINA","FIND","FINE","FING","FINI","FIRE","FIRM","FIRS","FISC","FISH","FIT","FITN","FIX","FLAG","FLAM","FLAS","FLAT","FLAV","FLEE","FLIG","FLIP","FLOA","FLOC","FLOO","FLOW","FLUI","FLUS","FLY","FOAM","FOCU","FOG","FOIL","FOLD","FOLL","FOOD","FOOT","FORC","FORE","FORG","FORK","FORT","FORU","FORW","FOSS","FOST","FOUN","FOX","FRAG","FRAM","FREQ","FRES","FRIE","FRIN","FROG","FRON","FROS","FROW","FROZ","FRUI","FUEL","FUN","FUNN","FURN","FURY","FUTU","GADG","GAIN","GALA","GALL","GAME","GAP","GARA","GARB","GARD","GARL","GARM","GAS","GASP","GATE","GATH","GAUG","GAZE","GENE","GENI","GENR","GENT","GENU","GEST","GHOS","GIAN","GIFT","GIGG","GING","GIRA","GIRL","GIVE","GLAD","GLAN","GLAR","GLAS","GLID","GLIM","GLOB","GLOO","GLOR","GLOV","GLOW","GLUE","GOAT","GODD","GOLD","GOOD","GOOS","GORI","GOSP","GOSS","GOVE","GOWN","GRAB","GRAC","GRAI","GRAN","GRAP","GRAS","GRAV","GREA","GREE","GRID","GRIE","GRIT","GROC","GROU","GROW","GRUN","GUAR","GUES","GUID","GUIL","GUIT","GUN","GYM","HABI","HAIR","HALF","HAMM","HAMS","HAND","HAPP","HARB","HARD","HARS","HARV","HAT","HAVE","HAWK","HAZA","HEAD","HEAL","HEAR","HEAV","HEDG","HEIG","HELL","HELM","HELP","HEN","HERO","HIDD","HIGH","HILL","HINT","HIP","HIRE","HIST","HOBB","HOCK","HOLD","HOLE","HOLI","HOLL","HOME","HONE","HOOD","HOPE","HORN","HORR","HORS","HOSP","HOST","HOTE","HOUR","HOVE","HUB","HUGE","HUMA","HUMB","HUMO","HUND","HUNG","HUNT","HURD","HURR","HURT","HUSB","HYBR","ICE","ICON","IDEA","IDEN","IDLE","IGNO","ILL","ILLE","ILLN","IMAG","IMIT","IMME","IMMU","IMPA","IMPO","IMPR","IMPU","INCH","INCL","INCO","INCR","INDE","INDI","INDO","INDU","INFA","INFL","INFO","INHA","INHE","INIT","INJE","INJU","INMA","INNE","INNO","INPU","INQU","INSA","INSE","INSI","INSP","INST","INTA","INTE","INTO","INVE","INVI","INVO","IRON","ISLA","ISOL","ISSU","ITEM","IVOR","JACK","JAGU","JAR","JAZZ","JEAL","JEAN","JELL","JEWE","JOB","JOIN","JOKE","JOUR","JOY","JUDG","JUIC","JUMP","JUNG","JUNI","JUNK","JUST","KANG","KEEN","KEEP","KETC","KEY","KICK","KID","KIDN","KIND","KING","KISS","KIT","KITC","KITE","KITT","KIWI","KNEE","KNIF","KNOC","KNOW","LAB","LABE","LABO","LADD","LADY","LAKE","LAMP","LANG","LAPT","LARG","LATE","LATI","LAUG","LAUN","LAVA","LAW","LAWN","LAWS","LAYE","LAZY","LEAD","LEAF","LEAR","LEAV","LECT","LEFT","LEG","LEGA","LEGE","LEIS","LEMO","LEND","LENG","LENS","LEOP","LESS","LETT","LEVE","LIAR","LIBE","LIBR","LICE","LIFE","LIFT","LIGH","LIKE","LIMB","LIMI","LINK","LION","LIQU","LIST","LITT","LIVE","LIZA","LOAD","LOAN","LOBS","LOCA","LOCK","LOGI","LONE","LONG","LOOP","LOTT","LOUD","LOUN","LOVE","LOYA","LUCK","LUGG","LUMB","LUNA","LUNC","LUXU","LYRI","MACH","MAD","MAGI","MAGN","MAID","MAIL","MAIN","MAJO","MAKE","MAMM","MAN","MANA","MAND","MANG","MANS","MANU","MAPL","MARB","MARC","MARG","MARI","MARK","MARR","MASK","MASS","MAST","MATC","MATE","MATH","MATR","MATT","MAXI","MAZE","MEAD","MEAN","MEAS","MEAT","MECH","MEDA","MEDI","MELO","MELT","MEMB","MEMO","MENT","MENU","MERC","MERG","MERI","MERR","MESH","MESS","META","METH","MIDD","MIDN","MILK","MILL","MIMI","MIND","MINI","MINO","MINU","MIRA","MIRR","MISE","MISS","MIST","MIX","MIXE","MIXT","MOBI","MODE","MODI","MOM","MOME","MONI","MONK","MONS","MONT","MOON","MORA","MORE","MORN","MOSQ","MOTH","MOTI","MOTO","MOUN","MOUS","MOVE","MOVI","MUCH","MUFF","MULE","MULT","MUSC","MUSE","MUSH","MUSI","MUST","MUTU","MYSE","MYST","MYTH","NAIV","NAME","NAPK","NARR","NAST","NATI","NATU","NEAR","NECK","NEED","NEGA","NEGL","NEIT","NEPH","NERV","NEST","NET","NETW","NEUT","NEVE","NEWS","NEXT","NICE","NIGH","NOBL","NOIS","NOMI","NOOD","NORM","NORT","NOSE","NOTA","NOTE","NOTH","NOTI","NOVE","NOW","NUCL","NUMB","NURS","NUT","OAK","OBEY","OBJE","OBLI","OBSC","OBSE","OBTA","OBVI","OCCU","OCEA","OCTO","ODOR","OFF","OFFE","OFFI","OFTE","OIL","OKAY","OLD","OLIV","OLYM","OMIT","ONCE","ONE","ONIO","ONLI","ONLY","OPEN","OPER","OPIN","OPPO","OPTI","ORAN","ORBI","ORCH","ORDE","ORDI","ORGA","ORIE","ORIG","ORPH","OSTR","OTHE","OUTD","OUTE","OUTP","OUTS","OVAL","OVEN","OVER","OWN","OWNE","OXYG","OYST","OZON","PACT","PADD","PAGE","PAIR","PALA","PALM","PAND","PANE","PANI","PANT","PAPE","PARA","PARE","PARK","PARR","PART","PASS","PATC","PATH","PATI","PATR","PATT","PAUS","PAVE","PAYM","PEAC","PEAN","PEAR","PEAS","PELI","PEN","PENA","PENC","PEOP","PEPP","PERF","PERM","PERS","PET","PHON","PHOT","PHRA","PHYS","PIAN","PICN","PICT","PIEC","PIG","PIGE","PILL","PILO","PINK","PION","PIPE","PIST","PITC","PIZZ","PLAC","PLAN","PLAS","PLAT","PLAY","PLEA","PLED","PLUC","PLUG","PLUN","POEM","POET","POIN","POLA","POLE","POLI","POND","PONY","POOL","POPU","PORT","POSI","POSS","POST","POTA","POTT","POVE","POWD","POWE","PRAC","PRAI","PRED","PREF","PREP","PRES","PRET","PREV","PRIC","PRID","PRIM","PRIN","PRIO","PRIS","PRIV","PRIZ","PROB","PROC","PROD","PROF","PROG","PROJ","PROM","PROO","PROP","PROS","PROT","PROU","PROV","PUBL","PUDD","PULL","PULP","PULS","PUMP","PUNC","PUPI","PUPP","PURC","PURI","PURP","PURS","PUSH","PUT","PUZZ","PYRA","QUAL","QUAN","QUAR","QUES","QUIC","QUIT","QUIZ","QUOT","RABB","RACC","RACE","RACK","RADA","RADI","RAIL","RAIN","RAIS","RALL","RAMP","RANC","RAND","RANG","RAPI","RARE","RATE","RATH","RAVE","RAW","RAZO","READ","REAL","REAS","REBE","REBU","RECA","RECE","RECI","RECO","RECY","REDU","REFL","REFO","REFU","REGI","REGR","REGU","REJE","RELA","RELE","RELI","RELY","REMA","REME","REMI","REMO","REND","RENE","RENT","REOP","REPA","REPE","REPL","REPO","REQU","RESC","RESE","RESI","RESO","RESP","RESU","RETI","RETR","RETU","REUN","REVE","REVI","REWA","RHYT","RIB","RIBB","RICE","RICH","RIDE","RIDG","RIFL","RIGH","RIGI","RING","RIOT","RIPP","RISK","RITU","RIVA","RIVE","ROAD","ROAS","ROBO","ROBU","ROCK","ROMA","ROOF","ROOK","ROOM","ROSE","ROTA","ROUG","ROUN","ROUT","ROYA","RUBB","RUDE","RUG","RULE","RUN","RUNW","RURA","SAD","SADD","SADN","SAFE","SAIL","SALA","SALM","SALO","SALT","SALU","SAME","SAMP","SAND","SATI","SATO","SAUC","SAUS","SAVE","SAY","SCAL","SCAN","SCAR","SCAT","SCEN","SCHE","SCHO","SCIE","SCIS","SCOR","SCOU","SCRA","SCRE","SCRI","SCRU","SEA","SEAR","SEAS","SEAT","SECO","SECR","SECT","SECU","SEED","SEEK","SEGM","SELE","SELL","SEMI","SENI","SENS","SENT","SERI","SERV","SESS","SETT","SETU","SEVE","SHAD","SHAF","SHAL","SHAR","SHED","SHEL","SHER","SHIE","SHIF","SHIN","SHIP","SHIV","SHOC","SHOE","SHOO","SHOP","SHOR","SHOU","SHOV","SHRI","SHRU","SHUF","SHY","SIBL","SICK","SIDE","SIEG","SIGH","SIGN","SILE","SILK","SILL","SILV","SIMI","SIMP","SINC","SING","SIRE","SIST","SITU","SIX","SIZE","SKAT","SKET","SKI","SKIL","SKIN","SKIR","SKUL","SLAB","SLAM","SLEE","SLEN","SLIC","SLID","SLIG","SLIM","SLOG","SLOT","SLOW","SLUS","SMAL","SMAR","SMIL","SMOK","SMOO","SNAC","SNAK","SNAP","SNIF","SNOW","SOAP","SOCC","SOCI","SOCK","SODA","SOFT","SOLA","SOLD","SOLI","SOLU","SOLV","SOME","SONG","SOON","SORR","SORT","SOUL","SOUN","SOUP","SOUR","SOUT","SPAC","SPAR","SPAT","SPAW","SPEA","SPEC","SPEE","SPEL","SPEN","SPHE","SPIC","SPID","SPIK","SPIN","SPIR","SPLI","SPOI","SPON","SPOO","SPOR","SPOT","SPRA","SPRE","SPRI","SPY","SQUA","SQUE","SQUI","STAB","STAD","STAF","STAG","STAI","STAM","STAN","STAR","STAT","STAY","STEA","STEE","STEM","STEP","STER","STIC","STIL","STIN","STOC","STOM","STON","STOO","STOR","STOV","STRA","STRE","STRI","STRO","STRU","STUD","STUF","STUM","STYL","SUBJ","SUBM","SUBW","SUCC","SUCH","SUDD","SUFF","SUGA","SUGG","SUIT","SUMM","SUN","SUNN","SUNS","SUPE","SUPP","SUPR","SURE","SURF","SURG","SURP","SURR","SURV","SUSP","SUST","SWAL","SWAM","SWAP","SWAR","SWEA","SWEE","SWIF","SWIM","SWIN","SWIT","SWOR","SYMB","SYMP","SYRU","SYST","TABL","TACK","TAG","TAIL","TALE","TALK","TANK","TAPE","TARG","TASK","TAST","TATT","TAXI","TEAC","TEAM","TELL","TEN","TENA","TENN","TENT","TERM","TEST","TEXT","THAN","THAT","THEM","THEN","THEO","THER","THEY","THIN","THIS","THOU","THRE","THRI","THRO","THUM","THUN","TICK","TIDE","TIGE","TILT","TIMB","TIME","TINY","TIP","TIRE","TISS","TITL","TOAS","TOBA","TODA","TODD","TOE","TOGE","TOIL","TOKE","TOMA","TOMO","TONE","TONG","TONI","TOOL","TOOT","TOP","TOPI","TOPP","TORC","TORN","TORT","TOSS","TOTA","TOUR","TOWA","TOWE","TOWN","TOY","TRAC","TRAD","TRAF","TRAG","TRAI","TRAN","TRAP","TRAS","TRAV","TRAY","TREA","TREE","TREN","TRIA","TRIB","TRIC","TRIG","TRIM","TRIP","TROP","TROU","TRUC","TRUE","TRUL","TRUM","TRUS","TRUT","TRY","TUBE","TUIT","TUMB","TUNA","TUNN","TURK","TURN","TURT","TWEL","TWEN","TWIC","TWIN","TWIS","TWO","TYPE","TYPI","UGLY","UMBR","UNAB","UNAW","UNCL","UNCO","UNDE","UNDO","UNFA","UNFO","UNHA","UNIF","UNIQ","UNIT","UNIV","UNKN","UNLO","UNTI","UNUS","UNVE","UPDA","UPGR","UPHO","UPON","UPPE","UPSE","URBA","URGE","USAG","USE","USED","USEF","USEL","USUA","UTIL","VACA","VACU","VAGU","VALI","VALL","VALV","VAN","VANI","VAPO","VARI","VAST","VAUL","VEHI","VELV","VEND","VENT","VENU","VERB","VERI","VERS","VERY","VESS","VETE","VIAB","VIBR","VICI","VICT","VIDE","VIEW","VILL","VINT","VIOL","VIRT","VIRU","VISA","VISI","VISU","VITA","VIVI","VOCA","VOIC","VOID","VOLC","VOLU","VOTE","VOYA","WAGE","WAGO","WAIT","WALK","WALL","WALN","WANT","WARF","WARM","WARR","WASH","WASP","WAST","WATE","WAVE","WAY","WEAL","WEAP","WEAR","WEAS","WEAT","WEB","WEDD","WEEK","WEIR","WELC","WEST","WET","WHAL","WHAT","WHEA","WHEE","WHEN","WHER","WHIP","WHIS","WIDE","WIDT","WIFE","WILD","WILL","WIN","WIND","WINE","WING","WINK","WINN","WINT","WIRE","WISD","WISE","WISH","WITN","WOLF","WOMA","WOND","WOOD","WOOL","WORD","WORK","WORL","WORR","WORT","WRAP","WREC","WRES","WRIS","WRIT","WRON","YARD","YEAR","YELL","YOU","YOUN","YOUT","ZEBR","ZERO","ZONE","ZOO"];

// Auto grid: fit as many pills as the printable area allows. The pill
// spans width x lenght, so a grid of c x r pills occupies
// c*width + (c-1)*spacing across. The usable width loses the front-left
// exclusion zone, so shift the whole grid right/up to stay clear of it.
usable = [bed[0] - 2 * bed_margin - exclusion[0] - prime_tower[0],
          bed[1] - 2 * bed_margin - exclusion[1]];
cols = columns > 0 ? columns
                   : floor((usable[0] + spacing) / (width + spacing));
rws  = rows > 0    ? rows
                   : floor((usable[1] + spacing) / (lenght + spacing));

// Offset the grid so it sits inside the printable area, clear of the
// front-left exclusion corner, roughly centered on the remaining space.
grid_span = [cols * width + (cols - 1) * spacing,
             rws * lenght + (rws - 1) * spacing];
origin = [-(bed[0] / 2) + bed_margin + exclusion[0]
            + (usable[0] - grid_span[0]) / 2 + width / 2,
           bed[1] / 2 - bed_margin
            - (usable[1] - grid_span[1]) / 2 - lenght / 2];

echo(str("grid: ", cols, " x ", rws, " = ", cols * rws, " pills, words ",
         first + 1, " to ", first + cols * rws * (double_sided ? 2 : 1)));

// Stadium (discorectangle) outline, optionally inset by `inset` per side.
// A plain hull() of two circles is far cheaper than offset() and produces
// far fewer segments.
module pill_outline(inset = 0) {
    hull()
        for (end = [-1, 1])
            translate([end * (width - lenght) / 2, 0])
                circle(r = lenght / 2 - inset);
}

module pill_shape() {
    linear_extrude(height)
        pill_outline();
}

module plate_id_outline() {
    hull()
        for (end = [-1, 1])
            translate([end * (plate_id_size[0] - plate_id_size[1]) / 2, 0])
                circle(r = plate_id_size[1] / 2);
}

// A separate two-color tile identifies the source plate after printing. It
// It sits directly below the last grid pill, clear of the lower tower band.
module plate_id() {
    label = str("P", plate_number, "/", plate_count);
    if (render_part == "both" || render_part == "base")
        color(base_color)
            linear_extrude(height)
                plate_id_outline();
    if (render_part == "both" || render_part == "text")
        color(text_color)
            translate([0, 0, height - 0.01])
                linear_extrude(text_height + 0.01)
                    resize([15, 5.2])
                        offset(r = text_weight)
                            text(label, size = font_size, font = font,
                                 halign = "center", valign = "center");
}

// Fit the actual expanded glyph outlines, rather than estimating from the
// character count. This keeps wide combinations such as AWKW inside the
// rounded pill while letting narrow words use the available face boldly.
module fitted_text(label) {
    target_width = len(label) <= 3 ? text_box_width[0] : text_box_width[1];
    resize([target_width, text_box_height])
        offset(r = text_weight)
            text(label, size = font_size, font = font,
                 halign = "center", valign = "center");
}

module pill(front_word, back_word, x, y) {
    // Face 0 is the top face; face 1 (only when double_sided) is the bottom
    // face, mirrored by rotating the pill 180 degrees.
    sides = double_sided ? [0, 1] : [0];
    face_word = [front_word, back_word];

    union() {
        if (render_part == "both" || render_part == "base")
            color(base_color)
                pill_shape();

        // Bold lettering raised directly from the flat pill base. There is no
        // inset panel or rim: the pill is simply a raft for the text.
        if ((render_part == "both" || render_part == "text")
            && front_word != "")
            for (side = sides)
                color(text_color)
                    rotate([0, 180 * side, 0])
                        translate([0, 0,
                                   side == 0 ? height - 0.01 : 0.01])
                            linear_extrude(text_height + 0.01)
                                fitted_text(face_word[side]);

        // Optional interlocks: mid-height bars bridging the gap to the
        // previous pill. Standalone pills avoid the rough snapped edges.
        if ((render_part == "both" || render_part == "base")
            && connected && x > 0)
            translate([-(width + spacing) / 2, 0, height / 2])
                cube([spacing + 2 * interlock_overlap, interlock, interlock],
                     center = true);
        if ((render_part == "both" || render_part == "base")
            && connected && y > 0)
            translate([0, (lenght + spacing) / 2, height / 2])
                cube([interlock, spacing + 2 * interlock_overlap, interlock],
                     center = true);
    }
}

// Slots past the end of the 2048-word list are rendered blank, so a full
// bed is always printed even when the word count doesn't divide evenly.
for (i = [0:cols * rws - 1]) {
    x = i % cols;
    y = floor(i / cols);
    front = first + i < len(words) ? words[first + i] : "";
    back = double_sided && first + i + 1024 < len(words)
               ? words[first + i + 1024] : "";
    translate([origin[0] + x * (width + spacing),
               origin[1] - y * (lenght + spacing), 0])
        pill(front, back, x, y);
}

if (show_plate_id)
    translate([origin[0] + (cols - 1) * (width + spacing),
               origin[1] - (rws - 1) * (lenght + spacing)
                   - lenght / 2 - spacing - plate_id_size[1] / 2,
               0])
        plate_id();

// Optional non-printing-scene helpers used to render README images.
if (show_build_plate)
    color([0.18, 0.21, 0.24])
        translate([0, 0, -0.11])
            cube([bed[0], bed[1], 0.2], center = true);

if (show_prime_tower)
    color([0.95, 0.35, 0.15, 0.75])
        translate([bed[0] / 2 - bed_margin - prime_tower[0] / 2,
                   bed[1] / 2 - bed_margin - prime_tower[1] / 2,
                   3])
            cube([prime_tower[0], prime_tower[1], 6], center = true);
