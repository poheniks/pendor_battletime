Source code for Battle Time 1.4 for Warband 1.153 by Egbert
Compiled with Warband Script Enhancer v3.1.4 by cmpxchg8b


Battle Time 1.4 for Warband 1.153 and WSE v3.1.4
Battle Time 1.31 for Warband 1.143 and WSE v2.8.1



This code is OSP, if you want to use it, don't ask permission, just give proper credit and let me know if you fix any bugs.
This mod requires Warband Script Enhancer: http://forums.taleworlds.com/index.php/topic,151194.0.html
Battle Time thread: http://forums.taleworlds.com/index.php/topic,150827.0.html
The source for v1 is also included for interested modders because it is designed quite differently. I do not recommend using v1 anymore, because storing values in high numbered registers can cause crashes.



To add Battle Time to your mod:
1. Copy the 3 extra module files (these only include code for Battle Time):
      module_coop_mission_templates.py
      module_coop_presentations.py
      module_coop_scripts.py
2. Search all files for #COOP BEGIN
3. Copy the parts from #COOP BEGIN to #COOP END into the corresponding module files
4. Copy the SceneObj folder to your mod (this overwrites scn_lair_steppe_bandits.sco to fix the ai mesh)
5. If you don't want the player's gold display in MP mode, copy game_variables.txt to your mod folder
6. Download and install the Warband Script Enhancer, and paste the header_operations_addon.py file at the end of your header_operations.py
7. In your mod's module.ini change damage_interrupt_attack_threshold_mp   = 3.0



Two current bugs in Native are noted in the code:
A bug where hero troops can't spawn in MP with both a bow and throwing weapons. The fix is marked by #ITEM BUG WORKAROUND.
A bug where clients may crash if they leave and rejoin a dedicated server. The fix is marked by #SERVER BUG WORKAROUND.



#TEMP SLOTS USED BY MOD#
slot_player_bot_type_1_wanted #MP server (for bot selection)

slot_troop_temp_slot        #MP server regular troop xp
slot_troop_current_rumor    #MP server troop class
all hero troops   slot 0 ~ 6, 19 ~ 34 #MP server

trp_temp_troop inventory slot 10 ~ 106 #MP server
trp_temp_troop   slot 0 ~ 18, 46 ~ 146, 147 ~ 246 #MP server/client

trp_temp_array_a  0 ~ 40   #MP server banners
trp_temp_array_b  0 ~ 40   #MP server banners

#PARTIES#
coop_temp_party_enemy_heroes       = "p_temp_casualties_2" #MP server/client
coop_temp_party_ally_heroes        = "p_temp_casualties_3" #MP server/client

coop_temp_party_enemy_begin        = 20 ~ 180 #MP server spawn parties
