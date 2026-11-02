
# ===================== EXTRA: icone ed effetti aggiunti video dopo video =====================
# Si unisce TRA vidkit_2.py e vidkit_3.py:  cat vidkit_1.py vidkit_2.py extra.py vidkit_3.py > vidkit.py
# Qui vanno SOLO le aggiunte nuove (icone stile 05, illustrazioni a pennello, effetti dei testi grandi), cosi'
# per salvarle nel progetto basta riscrivere questo file piccolo e non il kit intero.
# Icona:        def FR_nome(c,t): _card(c); _hl(c,t); fst(c,punti,i,t); acc(...); _arrow(c,t)   poi  FICONS["nome"]=FR_nome
# Effetto:      def fx_nome(L,tau,g,text): ...   poi  FX["nome"]=(fx_nome,2.0)   (+ PUNCH_RULES["nome"]=(...) se vuole il colpo di zoom)
