import json


def get_lua_string_for_player(parse, name, server, player_class) -> str:
    if player_class.lower().strip().replace(' ','') == "deathknight":
        class_string = '["class"] = "Death Knight"'
    else:
        class_string = f'["class"] = "{player_class.lower().strip().title()}" '
    naxx_string = f'["naxx"] = {{["dps"] = {parse["dps"]["naxx"] if parse["dps"]["naxx"] >= 10 else str(parse["dps"]["naxx"])+"0"},{"  " if parse["dps"]["naxx"]<100.0 else " "}["hps"] = {parse["hps"]["naxx"] if parse["hps"]["naxx"] > 10 else str(parse["hps"]["naxx"])+"0"}, ["dps_ilvl"] = {parse["dps_ilvl"]["naxx"] if parse["dps_ilvl"]["naxx"] >= 10 else str(parse["dps_ilvl"]["naxx"])+"0"},{"  " if parse["dps_ilvl"]["naxx"]<100.0 else " "}["hps_ilvl"] = {parse["hps_ilvl"]["naxx"] if parse["hps_ilvl"]["naxx"] > 10 else str(parse["hps_ilvl"]["naxx"])+"0"}}}'
    ulduar_string = f'["ulduar"] = {{["dps"] = {parse["dps"]["ulduar"] if parse["dps"]["ulduar"] >= 10 else str(parse["dps"]["ulduar"])+"0"},{"  " if parse["dps"]["ulduar"]<100.0 else " "}["hps"] = {parse["hps"]["ulduar"] if parse["hps"]["ulduar"] > 10 else str(parse["hps"]["ulduar"])+"0"}, ["dps_ilvl"] = {parse["dps_ilvl"]["ulduar"] if parse["dps_ilvl"]["ulduar"] >= 10 else str(parse["dps_ilvl"]["ulduar"])+"0"},{"  " if parse["dps_ilvl"]["ulduar"]<100.0 else " "}["hps_ilvl"] = {parse["hps_ilvl"]["ulduar"] if parse["hps_ilvl"]["ulduar"] > 10 else str(parse["hps_ilvl"]["ulduar"])+"0"}}}'
    toc_string = f'["toc"] = {{["dps"] = {parse["dps"]["toc"] if parse["dps"]["toc"] >= 10 else str(parse["dps"]["toc"])+"0"},{"  " if parse["dps"]["toc"]<100.0 else " "}["hps"] = {parse["hps"]["toc"] if parse["hps"]["toc"] > 10 else str(parse["hps"]["toc"])+"0"}, ["dps_ilvl"] = {parse["dps_ilvl"]["toc"] if parse["dps_ilvl"]["toc"] >= 10 else str(parse["dps_ilvl"]["toc"])+"0"},{"  " if parse["dps_ilvl"]["toc"]<100.0 else " "}["hps_ilvl"] = {parse["hps_ilvl"]["toc"] if parse["hps_ilvl"]["toc"] > 10 else str(parse["hps_ilvl"]["toc"])+"0"}}}'
    ony_string = f'["ony"] = {{["dps"] = {parse["dps"]["ony"] if parse["dps"]["ony"] >= 10 else str(parse["dps"]["ony"])+"0"},{"  " if parse["dps"]["ony"]<100.0 else " "}["hps"] = {parse["hps"]["ony"] if parse["hps"]["ony"] > 10 else str(parse["hps"]["ony"])+"0"}, ["dps_ilvl"] = {parse["dps_ilvl"]["ony"] if parse["dps_ilvl"]["ony"] >= 10 else str(parse["dps_ilvl"]["ony"])+"0"},{"  " if parse["dps_ilvl"]["ony"]<100.0 else " "}["hps_ilvl"] = {parse["hps_ilvl"]["ony"] if parse["hps_ilvl"]["ony"] > 10 else str(parse["hps_ilvl"]["ony"])+"0"}}}'
    if server.lower().strip().replace(' ','') == "bloodsailbuccaneers":
        string = f'WCL.DB.BloodsailBuccaneers["{name.title().strip()}"]' + ' '*(13-len(name.strip())) + f'=  {{ {class_string}, {naxx_string}, {ulduar_string}, {toc_string}, {ony_string} }}\n'
    else:
        string = f'WCL.DB.{server.lower().strip().title()}["{name.strip().title()}"]' + ' '*(13-len(name.strip())) + f'=  {{ {class_string},{" "*(12-len(player_class.strip()))}{naxx_string}, {ulduar_string}, {toc_string}, {ony_string} }}\n'
    return string



def get_lua_string_for_guild(guilds_dict, guild_name, server) -> str:
    guilds = guilds_dict
    
    def build_speed_string(size_string: str, progression_string: str, world_rank_string: str, region_rank_string: str, server_rank_string: str) -> str:
        a = '["speed"]    = {["size"] = "' + size_string + '", '
        if size_string == "-": a += ' '*8
        b = '["progression"] = "' + progression_string + '", ' + ' '*(7-len(progression_string))
        c = '["ranks"] = {["world"] = "' + world_rank_string + '",' + ' '*(30-len(world_rank_string))
        d = '["region"] = "' + region_rank_string + '",' + ' '*(28-len(region_rank_string))
        e = '["server"] = "' + server_rank_string + '"' + ' '*(27-len(server_rank_string))
        f = '}}'
        return a+b+c+d+e+f
    
    def build_progress_string(size_string: str, progression_string: str, world_rank_string: str, region_rank_string: str, server_rank_string: str) -> str:
        a = '["progress"] = {["size"] = "' + size_string + '", '
        if size_string == "-": a += ' '*8
        b = '["progression"] = "' + progression_string + '", ' + ' '*(7-len(progression_string))
        c = '["ranks"] = {["world"] = "' + world_rank_string + '",' + ' '*(30-len(world_rank_string))
        d = '["region"] = "' + region_rank_string + '",' + ' '*(28-len(region_rank_string))
        e = '["server"] = "' + server_rank_string + '"' + ' '*(27-len(server_rank_string))
        f = '}}'
        return a+b+c+d+e+f
    
    
    guild_data = guilds[guild_name]
    rankings = guild_data["rankings"]
    if "naxx" in rankings:
        naxx_rankings = rankings["naxx"]
        naxx_speed_rankings = naxx_rankings["speed"] if "speed" in naxx_rankings else None
        naxx_progress_rankings = naxx_rankings["progress"] if "progress" in naxx_rankings else None
    else:
        naxx_speed_rankings = None
        naxx_progress_rankings = None
    
    if "ulduar" in rankings:
        ulduar_rankings = rankings["ulduar"]
        ulduar_speed_rankings = ulduar_rankings["speed"] if "speed" in ulduar_rankings else None
        ulduar_progress_rankings = ulduar_rankings["progress"] if "progress" in ulduar_rankings else None
    else:
        ulduar_speed_rankings = None
        ulduar_progress_rankings = None
    
    if "toc" in rankings:
        toc_rankings = rankings["toc"]
        toc_speed_rankings = toc_rankings["speed"] if "speed" in toc_rankings else None
        toc_progress_rankings = toc_rankings["progress"] if "progress" in toc_rankings else None
    else:
        toc_speed_rankings = None
        toc_progress_rankings = None
    
    

    if naxx_speed_rankings is not None:
        naxx_speed_rankings_size = naxx_speed_rankings["size"]
        naxx_speed_amount = naxx_speed_rankings["progress_amount"]
        naxx_speed_total = naxx_speed_rankings["progress_total"]
        naxx_speed_world_rank = naxx_speed_rankings["world_rank"]
        naxx_speed_world_rank_color = naxx_speed_rankings["world_rank_color"].split('#')[-1].upper()
        naxx_speed_region_rank = naxx_speed_rankings["region_rank"]
        naxx_speed_region_rank_color = naxx_speed_rankings["region_rank_color"].split('#')[-1].upper()
        naxx_speed_server_rank = naxx_speed_rankings["server_rank"]
        naxx_speed_server_rank_color = naxx_speed_rankings["server_rank_color"].split('#')[-1].upper()
    else:
        naxx_speed_rankings_size = "-"
        naxx_speed_amount = 0
        naxx_speed_total = 17
        naxx_speed_world_rank = "-"
        naxx_speed_world_rank_color = "#666666".split('#')[-1].upper()
        naxx_speed_region_rank = "-"
        naxx_speed_region_rank_color = "#666666".split('#')[-1].upper()
        naxx_speed_server_rank = "-"
        naxx_speed_server_rank_color = "#666666".split('#')[-1].upper()

    naxx_speed_size_string = naxx_speed_rankings_size
    naxx_speed_progression_string = f'{naxx_speed_amount} / {naxx_speed_total}'
    naxx_speed_world_rank_string  = f'|cff".."{naxx_speed_world_rank_color}".."{naxx_speed_world_rank}".."|r'
    naxx_speed_region_rank_string = f'|cff".."{naxx_speed_region_rank_color}".."{naxx_speed_region_rank}".."|r'
    naxx_speed_server_rank_string = f'|cff".."{naxx_speed_server_rank_color}".."{naxx_speed_server_rank}".."|r'
    

    if naxx_progress_rankings is not None:
        naxx_progress_rankings_size = naxx_progress_rankings["size"]
        naxx_progress_amount = naxx_progress_rankings["progress_amount"]
        naxx_progress_total = naxx_progress_rankings["progress_total"]
        naxx_progress_world_rank = naxx_progress_rankings["world_rank"]
        naxx_progress_world_rank_color = naxx_progress_rankings["world_rank_color"].split('#')[-1].upper()
        naxx_progress_region_rank = naxx_progress_rankings["region_rank"]
        naxx_progress_region_rank_color = naxx_progress_rankings["region_rank_color"].split('#')[-1].upper()
        naxx_progress_server_rank = naxx_progress_rankings["server_rank"]
        naxx_progress_server_rank_color = naxx_progress_rankings["server_rank_color"].split('#')[-1].upper()
    else:
        naxx_progress_rankings_size = "-"
        naxx_progress_amount = 0
        naxx_progress_total = 17
        naxx_progress_world_rank = "-"
        naxx_progress_world_rank_color = "#666666".split('#')[-1].upper()
        naxx_progress_region_rank = "-"
        naxx_progress_region_rank_color = "#666666".split('#')[-1].upper()
        naxx_progress_server_rank = "-"
        naxx_progress_server_rank_color = "#666666".split('#')[-1].upper()

    naxx_progress_size_string = naxx_progress_rankings_size
    naxx_progress_progression_string = f'{naxx_progress_amount} / {naxx_progress_total}'
    naxx_progress_world_rank_string  = f'|cff".."{naxx_progress_world_rank_color}".."{naxx_progress_world_rank}".."|r'
    naxx_progress_region_rank_string = f'|cff".."{naxx_progress_region_rank_color}".."{naxx_progress_region_rank}".."|r'
    naxx_progress_server_rank_string = f'|cff".."{naxx_progress_server_rank_color}".."{naxx_progress_server_rank}".."|r'
    

    if ulduar_speed_rankings is not None:
        ulduar_speed_rankings_size = ulduar_speed_rankings["size"]
        ulduar_speed_amount = ulduar_speed_rankings["progress_amount"]
        ulduar_speed_total = ulduar_speed_rankings["progress_total"]
        ulduar_speed_world_rank = ulduar_speed_rankings["world_rank"]
        ulduar_speed_world_rank_color = ulduar_speed_rankings["world_rank_color"].split('#')[-1].upper()
        ulduar_speed_region_rank = ulduar_speed_rankings["region_rank"]
        ulduar_speed_region_rank_color = ulduar_speed_rankings["region_rank_color"].split('#')[-1].upper()
        ulduar_speed_server_rank = ulduar_speed_rankings["server_rank"]
        ulduar_speed_server_rank_color = ulduar_speed_rankings["server_rank_color"].split('#')[-1].upper()
    else:
        ulduar_speed_rankings_size = "-"
        ulduar_speed_amount = 0
        ulduar_speed_total = 54
        ulduar_speed_world_rank = "-"
        ulduar_speed_world_rank_color = "#666666".split('#')[-1].upper()
        ulduar_speed_region_rank = "-"
        ulduar_speed_region_rank_color = "#666666".split('#')[-1].upper()
        ulduar_speed_server_rank = "-"
        ulduar_speed_server_rank_color = "#666666".split('#')[-1].upper()

    ulduar_speed_size_string = ulduar_speed_rankings_size
    ulduar_speed_progression_string = f'{ulduar_speed_amount} / {ulduar_speed_total}'
    ulduar_speed_world_rank_string  = f'|cff".."{ulduar_speed_world_rank_color}".."{ulduar_speed_world_rank}".."|r'
    ulduar_speed_region_rank_string = f'|cff".."{ulduar_speed_region_rank_color}".."{ulduar_speed_region_rank}".."|r'
    ulduar_speed_server_rank_string = f'|cff".."{ulduar_speed_server_rank_color}".."{ulduar_speed_server_rank}".."|r'
    

    if ulduar_progress_rankings is not None:
        ulduar_progress_rankings_size = ulduar_progress_rankings["size"]
        ulduar_progress_amount = ulduar_progress_rankings["progress_amount"]
        ulduar_progress_total = ulduar_progress_rankings["progress_total"]
        ulduar_progress_world_rank = ulduar_progress_rankings["world_rank"]
        ulduar_progress_world_rank_color = ulduar_progress_rankings["world_rank_color"].split('#')[-1].upper()
        ulduar_progress_region_rank = ulduar_progress_rankings["region_rank"]
        ulduar_progress_region_rank_color = ulduar_progress_rankings["region_rank_color"].split('#')[-1].upper()
        ulduar_progress_server_rank = ulduar_progress_rankings["server_rank"]
        ulduar_progress_server_rank_color = ulduar_progress_rankings["server_rank_color"].split('#')[-1].upper()
    else:
        ulduar_progress_rankings_size = "-"
        ulduar_progress_amount = 0
        ulduar_progress_total = 54
        ulduar_progress_world_rank = "-"
        ulduar_progress_world_rank_color = "#666666".split('#')[-1].upper()
        ulduar_progress_region_rank = "-"
        ulduar_progress_region_rank_color = "#666666".split('#')[-1].upper()
        ulduar_progress_server_rank = "-"
        ulduar_progress_server_rank_color = "#666666".split('#')[-1].upper()

    ulduar_progress_size_string = ulduar_progress_rankings_size
    ulduar_progress_progression_string = f'{ulduar_progress_amount} / {ulduar_progress_total}'
    ulduar_progress_world_rank_string  = f'|cff".."{ulduar_progress_world_rank_color}".."{ulduar_progress_world_rank}".."|r'
    ulduar_progress_region_rank_string = f'|cff".."{ulduar_progress_region_rank_color}".."{ulduar_progress_region_rank}".."|r'
    ulduar_progress_server_rank_string = f'|cff".."{ulduar_progress_server_rank_color}".."{ulduar_progress_server_rank}".."|r'
    

    if toc_speed_rankings is not None:
        toc_speed_rankings_size = toc_speed_rankings["size"]
        toc_speed_amount = toc_speed_rankings["progress_amount"]
        toc_speed_total = toc_speed_rankings["progress_total"]
        toc_speed_world_rank = toc_speed_rankings["world_rank"]
        toc_speed_world_rank_color = toc_speed_rankings["world_rank_color"].split('#')[-1].upper()
        toc_speed_region_rank = toc_speed_rankings["region_rank"]
        toc_speed_region_rank_color = toc_speed_rankings["region_rank_color"].split('#')[-1].upper()
        toc_speed_server_rank = toc_speed_rankings["server_rank"]
        toc_speed_server_rank_color = toc_speed_rankings["server_rank_color"].split('#')[-1].upper()
    else:
        toc_speed_rankings_size = "-"
        toc_speed_amount = 0
        toc_speed_amount_mode = "Normal"
        toc_speed_total = 5
        toc_speed_world_rank = "-"
        toc_speed_world_rank_color = "#666666".split('#')[-1].upper()
        toc_speed_region_rank = "-"
        toc_speed_region_rank_color = "#666666".split('#')[-1].upper()
        toc_speed_server_rank = "-"
        toc_speed_server_rank_color = "#666666".split('#')[-1].upper()

    toc_speed_size_string = toc_speed_rankings_size
    toc_speed_progression_string = f'{toc_speed_amount}/{toc_speed_total}'
    toc_speed_world_rank_string  = f'|cff".."{toc_speed_world_rank_color}".."{toc_speed_world_rank}".."|r'
    toc_speed_region_rank_string = f'|cff".."{toc_speed_region_rank_color}".."{toc_speed_region_rank}".."|r'
    toc_speed_server_rank_string = f'|cff".."{toc_speed_server_rank_color}".."{toc_speed_server_rank}".."|r'
    

    if toc_progress_rankings is not None:
        toc_progress_rankings_size = toc_progress_rankings["size"]
        toc_progress_amount = toc_progress_rankings["progress_amount"]
        toc_progress_amount_mode = toc_progress_rankings["progress_amount_mode"]
        toc_progress_total = toc_progress_rankings["progress_total"]
        toc_progress_world_rank = toc_progress_rankings["world_rank"]
        toc_progress_world_rank_color = toc_progress_rankings["world_rank_color"].split('#')[-1].upper()
        toc_progress_region_rank = toc_progress_rankings["region_rank"]
        toc_progress_region_rank_color = toc_progress_rankings["region_rank_color"].split('#')[-1].upper()
        toc_progress_server_rank = toc_progress_rankings["server_rank"]
        toc_progress_server_rank_color = toc_progress_rankings["server_rank_color"].split('#')[-1].upper()
    else:
        toc_progress_rankings_size = "-"
        toc_progress_amount = 0
        toc_progress_amount_mode = "Normal"
        toc_progress_total = 5
        toc_progress_world_rank = "-"
        toc_progress_world_rank_color = "#666666".split('#')[-1].upper()
        toc_progress_region_rank = "-"
        toc_progress_region_rank_color = "#666666".split('#')[-1].upper()
        toc_progress_server_rank = "-"
        toc_progress_server_rank_color = "#666666".split('#')[-1].upper()

    toc_progress_size_string = toc_progress_rankings_size
    toc_progress_progression_string = f'{toc_progress_amount}/{toc_progress_total} {toc_progress_amount_mode}'
    toc_progress_world_rank_string  = f'|cff".."{toc_progress_world_rank_color}".."{toc_progress_world_rank}".."|r'
    toc_progress_region_rank_string = f'|cff".."{toc_progress_region_rank_color}".."{toc_progress_region_rank}".."|r'
    toc_progress_server_rank_string = f'|cff".."{toc_progress_server_rank_color}".."{toc_progress_server_rank}".."|r'


    naxx_speed_string = build_speed_string(naxx_speed_size_string, naxx_speed_progression_string, naxx_speed_world_rank_string, naxx_speed_region_rank_string, naxx_speed_server_rank_string)
    naxx_progress_string = build_progress_string(naxx_progress_size_string, naxx_progress_progression_string, naxx_progress_world_rank_string, naxx_progress_region_rank_string, naxx_progress_server_rank_string)
    ulduar_speed_string = build_speed_string(ulduar_speed_size_string, ulduar_speed_progression_string, ulduar_speed_world_rank_string, ulduar_speed_region_rank_string, ulduar_speed_server_rank_string)
    ulduar_progress_string = build_progress_string(ulduar_progress_size_string, ulduar_progress_progression_string, ulduar_progress_world_rank_string, ulduar_progress_region_rank_string, ulduar_progress_server_rank_string)
    toc_speed_string = build_speed_string(toc_speed_size_string, toc_speed_progression_string, toc_speed_world_rank_string, toc_speed_region_rank_string, toc_speed_server_rank_string)
    toc_progress_string = build_progress_string(toc_progress_size_string, toc_progress_progression_string, toc_progress_world_rank_string, toc_progress_region_rank_string, toc_progress_server_rank_string)

    base_string = f'WCL.DB.{server.lower().strip().title()}.Guilds["{guild_name}"] = '
    guild_string = base_string + '{\n\t["naxx"] = {\n\t\t' + naxx_speed_string + ',\n\t\t' + naxx_progress_string + '},\n\t["ulduar"] = {\n\t\t' + ulduar_speed_string + ',\n\t\t' + ulduar_progress_string + '},\n\t["toc"] = {\n\t\t' + toc_speed_string + ',\n\t\t' + toc_progress_string  + '},\n}'

    return guild_string+'\n'
