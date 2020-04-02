def plot(_step, agent_decisions, compressors):
    for k in compressors:
        cs = compressors[k]
        _from, _to = k.split("^")
        gas = agent_decisions["gas"]["CS"][k]
        L_min_pi = cs["L_min_pi"]
        L_min_phi = cs["L_min_phi"]
        L_max_pi = cs["L_max_pi"]
        eta = cs["eta"]
        p_i_min = cs["p_i_min"]
        p_i_max = cs["p_i_max"]
        pi_1 = cs["pi_1"]
        pi_2 = cs["pi_2"]
        phi_max = cs["phi_max"]
        phi_min = cs["phi_min"]

        cmd = ";".join([
"gnuplot -e \"set term pdfcairo enhanced font 'Calibri Light, 10'",
"set output '%s/CS_%s_%s_%s.pdf'" % (output, _from, _to, _step),
# title
"set title '{/:Bold Verdichter %s -> %s (%s)}'" % (_from, _to, _step),
# labels
"set xlabel 'Fluss {/Symbol f}/m^3/s'",
"set ylabel 'Druckverh\344ltnis {/Symbol p}/1'",

# LINES
"plot [0:%f] %s" % (cs["phi_max"] + 1, " ".join([

    # l min line
    "[0:%f]" % (cs["L_max_pi"] + 0.5),
    "- %f / %f * x + %f title 'L_{min}' lt 1 lw 2, " % (
        L_min_pi,
        L_min_phi,
        L_min_pi
    ),

    # l max line
    "- %f / %f * x + %f title 'L_{max}' lt 1 lw 2, " % (
        L_min_pi,
        L_min_phi,
        L_max_axis_intercept(
            L_max_pi,
            eta,
            p_i_min,
            p_i_max,
            p_old(_from)
        )
    ),

    # l gas line
    "(1 - %f) * ((-%f / %f) * x + %f) + %f * ((-%f / %f) * x + %f) dashtype 4 lt 3 title 'L_{gas}', " % (
        gas,
        L_min_pi,
        L_min_phi,
        L_min_pi,
        gas,
        L_min_pi,
        L_min_phi,
        L_max_axis_intercept(
            L_max_pi,
            eta,
            p_i_min,
            p_i_max,
            p_old(_from)
        )
    ),

    # pi 1 line
    "%f dashtype 3 lt 1 title '{/Symbol p}_1', " % (pi_1),

    # L_max_max line
    "(-%f / %f) * x + %f dashtype 3 lt 1 lw 1 title 'L_{MAX}', " % (
        L_min_pi,
        L_min_phi,
        L_max_axis_intercept(
            L_max_pi,
            eta,
            p_i_min,
            p_i_max,
            p_i_min
        )
    ),

    # ulim line
    "(%f - %f) / %f * x + %f lt 1 lw 2 title 'ulim', " % (
        pi_1,
        pi_2,
        phi_max,
        pi_2
    ),

    # (old) pressure_to / pressure_from line
    "(%f / %f) dashtype 4 lt 3 title 'p_{out} / p_{in}'" % (
        p_old(_to),
        p_old(_from)
    ),
])),
# phi_min line
"set arrow from %f,0 to %f,%f*2 nohead dashtype 2 lc rgb 'black' " % (
    phi_min,
    phi_min,
    pi_2
),

# phi_max line
"set arrow from %f,0 to %f,%f nohead dashtype 2 lc rgb 'black'" % (
    phi_max,
    phi_max,
    pi_2
),

# TICKS
# add L_max_axis_intercept value as tic
"set ytics add('L_{max\\_axis\\_int}(%f))' %f) " % (
    round(10 * p_old(_from)) / 10,
    L_max_axis_intercept(
        L_max_pi,
        eta,
        p_i_min,
        p_i_max,
        p_old(_from)
    )
),

# add pi_2 value as a tic
"set ytics add ('{/Symbol p}_2' %f) " % pi_2,

# add pi_1 value as a tic
"set ytics add ('{/Symbol p}_1' %f) " % pi_1,

# add L_min_pi value as a tic
"set ytics add ('{/Symbol p}_{\\_min}' %f)" % L_min_pi,

# add phi_min value as tic
"set xtics add ('{/Symbol f}_{min}' %f)" % phi_min,

# add phi_max value as a tic
"set xtics add ('{/Symbol f}_{max}' %f)" % phi_max,

# add L_phi_min value as a tic
"set xtics add ('L_{/Symbol f}_{\\_min}' %f)" % L_min_phi,


# POINTS
# add interception point
"set label at %f, %f '' point pointtype 7 pointsize 1" % (
    intercept(
        L_min_pi,
        L_min_phi,
        p_i_min,
        p_i_max,
        L_max_pi,
        eta,
        gas,
        p_old(_from),
        p_old(_to)
    ),
    (p_old(_to) / p_old(_from))
),


# FINILIZE
"set output '%s/CS_%s_%s_%s.pdf'" % (output, _from, _to, _step),
"replot; \""
        ])

        os.system(cmd)
