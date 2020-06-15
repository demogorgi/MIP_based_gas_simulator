def get_human_decisions(agent_decisions,i):
        if i == 0:
           agent_decisions["entry_nom"]["S"]["EN_aux0^EN"] = [1100]
           agent_decisions["entry_nom"]["S"]["EH_aux0^EH"] = [0]
        if i == 10:
           agent_decisions["entry_nom"]["S"]["EN_aux0^EN"] = [0]
           agent_decisions["entry_nom"]["S"]["EH_aux0^EH"] = [1100]
           agent_decisions["compressor"]["CS"]["N22^N23"] = 0
           agent_decisions["gas"]["CS"]["N22^N23"] = 0
           agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 191
        #if i >= 50:
        #   agent_decisions["gas"]["CS"]["N22^N23"] = 0.2
        #if i >= 100:
        #   agent_decisions["gas"]["CS"]["N22^N23"] = 0.3
        #if i >= 150:
        #   agent_decisions["gas"]["CS"]["N22^N23"] = 0.4
        #if i >= 200:
        #   agent_decisions["gas"]["CS"]["N22^N23"] = 0.5
        #if i >= 250:
        #   agent_decisions["gas"]["CS"]["N22^N23"] = 0.6
        #if i >= 300:
        #   agent_decisions["gas"]["CS"]["N22^N23"] = 0.7
        #if i >= 350:
        #   agent_decisions["gas"]["CS"]["N22^N23"] = 0.8
        #if i >= 400:
        #   agent_decisions["gas"]["CS"]["N22^N23"] = 0.9
        #if i >= 450:
        #   agent_decisions["gas"]["CS"]["N22^N23"] = 1.0
        #
        #if i == 40:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 580
        #if i == 50:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 560
        #if i == 60:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 540
        #if i == 70:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 520
        #if i == 80:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 500
        #if i == 90:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 450
        #if i == 100:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 400
        #if i == 110:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 350
        #if i == 120:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 300
        #if i == 130:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 280
        #if i == 140:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 260
        #if i == 150:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 240
        #if i == 160:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 200
        #if i == 170:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 175
        #if i == 180:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 150
        #if i == 190:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 100
        #if i == 190:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 6
        #if i == 200:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 4
        #if i == 210:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 2
        #if i == 220:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 1
        #if i == 220:
        #   agent_decisions["zeta"]["RE"]["N25^N26_aux"] = 0.1

