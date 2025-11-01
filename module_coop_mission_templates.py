print "Exporting coop mission templates"

from header_common import *
from header_operations import *
from header_mission_templates import *
from header_animations import *
from header_sounds import *
from header_music import *
from header_items import *
from module_constants import *

#from module_mission_templates import *


####################################################################################################################
#   Each mission-template is a tuple that contains the following fields:
#  1) Mission-template id (string): used for referencing mission-templates in other files.
#     The prefix mt_ is automatically added before each mission-template id
#
#  2) Mission-template flags (int): See header_mission-templates.py for a list of available flags
#  3) Mission-type(int): Which mission types this mission template matches.
#     For mission-types to be used with the default party-meeting system,
#     this should be 'charge' or 'charge_with_ally' otherwise must be -1.
#     
#  4) Mission description text (string).
#  5) List of spawn records (list): Each spawn record is a tuple that contains the following fields:
#    5.1) entry-no: Troops spawned from this spawn record will use this entry
#    5.2) spawn flags.
#    5.3) alter flags. which equipment will be overriden
#    5.4) ai flags.
#    5.5) Number of troops to spawn.
#    5.6) list of equipment to add to troops spawned from here (maximum 8).
#  6) List of triggers (list).
#     See module_triggers.py for infomation about triggers.
#
#  Please note that mission templates is work in progress and can be changed in the future versions.
# 
####################################################################################################################


coop_server_check_polls = (
  1, 5, 0,
  [
    (multiplayer_is_server),
    (eq, "$g_multiplayer_poll_running", 1),
    (eq, "$g_multiplayer_poll_ended", 0),
    (store_mission_timer_a, ":mission_timer"),
    (store_add, ":total_votes", "$g_multiplayer_poll_no_count", "$g_multiplayer_poll_yes_count"),
    (this_or_next|eq, ":total_votes", "$g_multiplayer_poll_num_sent"),
    (gt, ":mission_timer", "$g_multiplayer_poll_end_time"),
    (call_script, "script_cf_multiplayer_evaluate_poll"),
    ],
  [
    (assign, "$g_multiplayer_poll_running", 0),
    ])


coop_store_respawn_as_bot = (  
      ti_on_agent_killed_or_wounded, 0, 0, [(multiplayer_is_server)],
       [
         (store_trigger_param_1, ":dead_agent_no"),
         (try_begin),#store player location for respawn as bot
           
           (agent_is_human, ":dead_agent_no"),
           (neg|agent_is_non_player, ":dead_agent_no"),

           (ge, ":dead_agent_no", 0),
           (agent_get_player_id, ":dead_agent_player_id", ":dead_agent_no"),
           (ge, ":dead_agent_player_id", 0),

           (set_fixed_point_multiplier, 100),

           (agent_get_player_id, ":dead_agent_player_id", ":dead_agent_no"),
           (agent_get_position, pos0, ":dead_agent_no"),

           (position_get_x, ":x_coor", pos0),
           (position_get_y, ":y_coor", pos0),
           (position_get_z, ":z_coor", pos0),
         
           (player_set_slot, ":dead_agent_player_id", slot_player_death_pos_x, ":x_coor"),
           (player_set_slot, ":dead_agent_player_id", slot_player_death_pos_y, ":y_coor"),
           (player_set_slot, ":dead_agent_player_id", slot_player_death_pos_z, ":z_coor"),
         (try_end), 
 
    ])



coop_respawn_as_bot = (  
      2, 0, 0, [
        (multiplayer_is_server),
        (eq, "$g_multiplayer_player_respawn_as_bot", 1),
      ],#respawn as bot
       [
       #spawning as a bot (if option ($g_multiplayer_player_respawn_as_bot) is 1)
         (get_max_players, ":num_players"),
         (try_for_range, ":player_no", 0, ":num_players"),
           (player_is_active, ":player_no"),
           (neg|player_is_busy_with_menus, ":player_no"),
           (try_begin),
            (player_get_team_no, ":player_team", ":player_no"),

            (assign, ":continue", 0),
            (player_get_agent_id, ":player_agent", ":player_no"),
            (try_begin),
             (ge, ":player_agent", 0),
             (neg|agent_is_alive, ":player_agent"),
             (assign, ":continue", 1),
            (else_try),
             (lt, ":player_agent", 0),
             (player_get_slot, ":player_selected_troop", ":player_no", slot_player_coop_selected_troop),
             (le, ":player_selected_troop", 0),
             (assign, ":continue", 2),
            (try_end),
            (gt, ":continue", 0),

             # (agent_get_time_elapsed_since_removed, ":elapsed_time", ":player_agent"),
             # (gt, ":elapsed_time", "$g_multiplayer_respawn_period"),

             (assign, ":is_found", 0),
             (try_for_agents, ":cur_agent"),
               (eq, ":is_found", 0),
               (agent_is_alive, ":cur_agent"),
               (agent_is_human, ":cur_agent"),
               (agent_is_non_player, ":cur_agent"),
               (agent_get_team ,":cur_team", ":cur_agent"),
               (eq, ":cur_team", ":player_team"),
               (agent_get_position, pos0, ":cur_agent"),
               (assign, ":is_found", 1),
             (try_end),

            (try_begin), #if we have not spawned store pos of ally
             (eq, ":continue", 2),
             (set_fixed_point_multiplier, 100),
             (position_get_x, ":x_coor", pos0),
             (position_get_y, ":y_coor", pos0),
             (position_get_z, ":z_coor", pos0),
             (player_set_slot, ":player_no", slot_player_death_pos_x, ":x_coor"),
             (player_set_slot, ":player_no", slot_player_death_pos_y, ":y_coor"),
             (player_set_slot, ":player_no", slot_player_death_pos_z, ":z_coor"),
            (try_end),

             (try_begin),
               (eq, ":is_found", 1),
               (call_script, "script_find_most_suitable_bot_to_control", ":player_no"),
               (player_control_agent, ":player_no", reg0),
             (try_end),
           (try_end),
         (try_end),
         ])



# Trigger Param 1: damage inflicted agent_id
# Trigger Param 2: damage dealer agent_id
# Trigger Param 3: inflicted damage
# Register 0: damage dealer item_id
# Position Register 0: position of the blow
#                      rotation gives the direction of the blow
# Trigger result: if returned result is greater than or equal to zero, inflicted damage is set to the value specified by the module.
coop_server_reduce_damage = (
  ti_on_agent_hit, 0, 0,
    [    
      (multiplayer_is_server),
      (eq, "$coop_reduce_damage", 1),
    ],
    [
        (store_trigger_param_1, ":hit_agent"),
        (store_trigger_param_2, ":attacker_agent"),
        (store_trigger_param_3, ":damage"),
        # (assign, ":weapon", reg0),
        (gt, ":damage", 0), #dont do anything for 0 damage
        (agent_is_human, ":hit_agent"),
        (agent_is_human, ":attacker_agent"),
        (neg|agent_is_non_player, ":hit_agent"), #damage is for player agent
        (store_div, ":new_damage", ":damage", 4),
        (set_trigger_result, ":new_damage"),
    ])


coop_mission_templates = [

# USE FOR COOP BATTLE
    (
    "coop_battle",mtf_battle_mode,-1,
    "You lead your men to battle.",
    [     #need spawns 0-63 in multiplayer mode
      (0,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (1,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (2,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (3,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (4,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (5,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (6,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (7,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),

      (8,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (9,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (10,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (11,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),#NEW
      (12,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (13,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (14,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (15,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (16,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (17,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (18,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (19,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (20,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (21,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (22,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (23,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (24,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (25,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (26,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (27,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (28,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (29,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (30,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (31,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (32,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (33,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (34,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (35,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (36,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (37,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (38,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (39,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (40,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (41,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (42,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (43,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (44,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (45,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (46,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (47,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (48,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (49,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (50,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (51,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (52,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (53,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (54,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (55,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (56,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (57,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (58,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (59,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (60,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (61,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (62,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (63,mtef_visitor_source,0,aif_start_alarmed,1,[]),

     ],
    [

      coop_server_check_polls,
      coop_server_reduce_damage,
      coop_respawn_as_bot,
      coop_store_respawn_as_bot,


#mordr does not work in MP = SCRIPT ERROR ON OPCODE 1785: Invalid Group ID: 1;
     # common_battle_order_panel,
     # common_battle_order_panel_tick,

#multiplayer_once_at_the_first_frame
      
      (ti_server_player_joined, 0, 0, [],
       [
        (store_trigger_param_1, ":player_no"),
       #  (call_script, "script_multiplayer_server_player_joined_common", ":player_no"), #dont clear slots
        (call_script, "script_multiplayer_send_initial_information", ":player_no"),
        (call_script, "script_coop_server_player_joined_common", ":player_no"),

         ]),



      (ti_before_mission_start, 0, 0, [],
       [
         (assign, "$g_multiplayer_game_type", multiplayer_game_type_coop_battle),
#remove
#         (call_script, "script_multiplayer_server_before_mission_start_common"), #dont set time of day, reset commanded troops
 #        (call_script, "script_multiplayer_init_mission_variables"),
##########

         (call_script, "script_coop_init_mission_variables"),
         (call_script, "script_initialize_banner_info"),


         (assign, "$g_waiting_for_confirmation_to_terminate", 0),
         (assign, "$g_round_ended", 0),
         (assign, "$coop_winner_team", -1),
         (assign, "$coop_battle_started", 0),

        # (assign, reg1, "$coop_time_of_day"), 
        # (assign, reg2, "$coop_cloud"), 
        # (assign, reg3, "$coop_haze"), 
        # (display_message, "@time {reg1} cloud {reg2} haze {reg3}"),

          #set_weather
         (scene_set_day_time, "$coop_time_of_day"),
	       (set_global_cloud_amount, "$coop_cloud"),
	       (set_global_haze_amount, "$coop_haze"),

          #removed set_fog_distance needs correct color in 1.143
         # (try_begin),
           # (gt, "$coop_cloud", 65), #if cloud cover
           # (lt,  "$coop_haze", 91), #not heavy fog
           # (set_global_haze_amount, 95), #remove sunlight
         # (try_end),

         (assign, ":rain_amount", "$coop_cloud"),
         (assign, ":rain_type", "$coop_rain"),
         (try_begin),
           (lt, ":rain_amount", 75), #less than = no rain
           (assign, ":rain_amount", 0),
           (assign, ":rain_type", 0),
         (try_end),
         (set_rain, ":rain_type" , ":rain_amount"), #1=rain 2=snow

         ]),

      (ti_after_mission_start, 0, 0, [], 
       [
         (call_script, "script_initialize_all_scene_prop_slots"),
         (call_script, "script_multiplayer_initialize_belfry_wheel_rotations"),
         (call_script, "script_multiplayer_move_moveable_objects_initial_positions"),
         (assign, "$g_multiplayer_bot_type_1_wanted", 1),#set player wants all troops in party (host will override clients)#this should be optional

        # (assign, "$g_multiplayer_ready_for_spawning_agent", 1), #set by start battle command in presentations

          #removed set_fog_distance needs correct color in 1.143
         # (try_begin),#limit fog
           # (gt, "$coop_cloud", 65), #if cloud cover
           # (lt,  "$coop_haze", 91), #not heavy fog
           # (try_begin),
             # (eq,  "$coop_rain", 2), #if snow
             # (set_fog_distance, 200), #set fog closer
           # (else_try),
             # (set_fog_distance, 600),
           # (try_end),
         # (try_end),

        (try_begin),
          (multiplayer_is_server),
          (start_presentation, "prsnt_coop_start_battle"),
        (else_try),
          (multiplayer_get_my_player, ":my_player_no"),
          (ge, ":my_player_no", 0),
          (player_is_admin, ":my_player_no"),
          (start_presentation, "prsnt_coop_start_battle"),
        (try_end),

        (try_begin),
          (multiplayer_is_server),
          (assign, "$coop_reinforce_size", 10),
          (assign, "$coop_reinforce", 1),
          (assign, "$coop_alive_team1", 0),#store count for reinforcement spawn
          (assign, "$coop_alive_team2", 0),


            #init spawn positions
          (entry_point_get_position, pos25, 32),
          (copy_position, pos26, pos25),
          (position_move_y, pos26, 600),
          (copy_position, pos27, pos25),
          (position_move_y, pos27, 1500),

          (entry_point_get_position, pos30, 0),
          (copy_position, pos31, pos30),
          (position_move_y, pos31, 600),
          (copy_position, pos32, pos30),
          (position_move_y, pos32, 1500),

            (try_begin),
              (eq, "$coop_battle_type", coop_battle_type_village_player_attack),
              (assign, ":ally", 1), 
              (assign, ":enemy", 2),#inside village
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_village_player_defend),
              (assign, ":ally", 2),#inside village
              (assign, ":enemy", 1),
            (else_try),
              (assign, ":ally", 0),
              (assign, ":enemy", 32),
            (try_end),

           (entry_point_get_position, pos2, ":enemy"),
           (entry_point_get_position, pos3, ":ally"),
           (position_set_z_to_ground_level, pos2),
           (position_set_z_to_ground_level, pos3),

           (set_spawn_position, pos2),
           (spawn_scene_prop, "spr_coop_inventory", 0),   

           (set_spawn_position, pos3),
           (spawn_scene_prop, "spr_coop_inventory", 0),  
           (assign, "$coop_inventory_box", reg0),

        (try_end),

        ]),



 #multiplayer_server_spawn_bots
      (0, 0, 0, [],
       [
        (try_begin),
        (multiplayer_is_server),
        (eq, "$g_multiplayer_ready_for_spawning_agent", 1),


        (assign, ":battle_size", "$coop_battle_size"),
        (try_begin), 
          (eq, "$coop_battle_type", coop_battle_type_bandit_lair),
          (assign, ":battle_size", coop_min_battle_size),
        (try_end),

        #regulate troop spawn
        (store_add, ":total_bots", "$coop_alive_team1", "$coop_alive_team2"),
        (store_sub, ":reinforce_bots", ":battle_size", "$coop_reinforce_size"),#when less troops than battle size
        (try_begin),
          (le, ":total_bots", ":reinforce_bots"), #when total alive < battle size - reinforce size
          (assign, "$coop_reinforce", 1),
        (try_end),
        (try_begin),
          (ge, ":total_bots", ":battle_size"), 
          (assign, "$coop_reinforce", 0),
        (try_end),

        (try_begin),
          (eq, "$coop_reinforce", 1), #ready for reinforcements

          #pick team by size
          (store_add, ":total_req", "$coop_num_bots_team_1", "$coop_num_bots_team_2"),
          (gt, ":total_req", 0), #reserves 

          (assign, ":alive_team1", "$coop_alive_team1"),
          (assign, ":alive_team2", "$coop_alive_team2"),
          (val_max, ":alive_team1", 1),
          (val_mul, ":alive_team2", 1000),
          (store_div, ":ratio_current", ":alive_team2", ":alive_team1"), 

          (try_begin),
            (this_or_next|eq, "$coop_num_bots_team_2", 0), #skip ratio if other team has no reinforcements
            (ge, ":ratio_current", "$coop_team_ratio"),
            (gt, "$coop_num_bots_team_1", 0),
            (assign, ":selected_team", 0),#add to team 1
          (else_try),
            (gt, "$coop_num_bots_team_2", 0),
            (assign, ":selected_team", 1),#add to team 2
          (try_end),



          #if one team is almost out of troops, choose that team
          (try_begin), #use one try so small armies don't override
            (le, "$coop_alive_team1", "$coop_reinforce_size"),
            (gt, "$coop_num_bots_team_1", 0),
            (assign, ":selected_team", 0),
          (else_try),
            (le, "$coop_alive_team2", "$coop_reinforce_size"),
            (gt, "$coop_num_bots_team_2", 0),
            (assign, ":selected_team", 1),
          (try_end),

          (call_script, "script_coop_find_bot_troop_for_spawn", ":selected_team"),
          (assign, ":selected_troop", reg0),

          (try_begin),
            (eq, ":selected_team", 0),     
            (try_begin),
              (eq, "$coop_battle_type", coop_battle_type_village_player_attack),
              (assign, reg0, 2),#peasants inside village
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_village_player_defend),
              (assign, reg0, 1),#bandits outside village
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_bandit_lair),
              (store_random_in_range, ":random_entry_point", 2, 11),
              (assign, reg0, ":random_entry_point"),#bandits 
            (else_try),
              (assign, reg0, 32),#spawn point 32
            (try_end),
          (else_try),
            (try_begin),#player team
              (eq, "$coop_battle_type", coop_battle_type_village_player_attack),
              (assign, reg0, 1), #player outside village
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_village_player_defend),
              (assign, reg0, 2),#player inside village

#NEW
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_bandit_lair),
              (assign, reg0, 11),#player inside village

            (else_try),
              (assign, reg0, 0),#spawn point 0
            (try_end),
          (try_end),

          (store_current_scene, ":cur_scene"),
          (modify_visitors_at_site, ":cur_scene"),
          (add_visitors_to_current_scene, reg0, ":selected_troop", 1, ":selected_team", -1),#don't assign group at spawn
          (assign, "$g_multiplayer_ready_for_spawning_agent", 0),

          (try_begin),
            (eq, ":selected_team", 0),
            (val_sub, "$coop_num_bots_team_1", 1),
          (else_try),
            (eq, ":selected_team", 1),
            (val_sub, "$coop_num_bots_team_2", 1),
          (try_end),
        (try_end),    
        (try_end),    
        ]),
 


#multiplayer_server_manage_bots
      (3, 0, 0, [], 
       [
        (multiplayer_is_server),
        (store_mission_timer_a, ":seconds_past_since_round_started"),

        #this can be used to make the bigger team charge first
        # (try_begin),#pick attacker to charge
          # (gt, "$coop_alive_team1", "$coop_alive_team2"), 
          # (assign, ":team_charge", 0),
        # (else_try),
          # (assign, ":team_charge", 1),
        # (try_end),

          # (assign, ":hold_time", "$coop_alive_team1"),
          # (val_max, ":hold_time", "$coop_alive_team2"), 
          # (val_div, ":hold_time", 5), #larger team / 5
          (store_add, ":hold_time", "$coop_alive_team1", "$coop_alive_team2"),
          (val_div, ":hold_time", 2), 
          (val_clamp, ":hold_time", 10, 41),

        (try_for_agents, ":cur_agent"),
          (agent_is_non_player, ":cur_agent"),
          (agent_is_human, ":cur_agent"),
          (agent_is_alive, ":cur_agent"),
          (call_script, "script_coop_change_leader_of_bot", ":cur_agent"),

          # (agent_get_group, ":agent_group", ":cur_agent"),
          # (agent_get_team, ":agent_team", ":cur_agent"),
          (try_begin),
            (this_or_next|eq, "$coop_battle_type", coop_battle_type_village_player_attack), #no delay for village raid
            (eq, "$coop_battle_type", coop_battle_type_village_player_defend), #village battle
            (agent_clear_scripted_mode, ":cur_agent"),
          (else_try),
            (gt, ":seconds_past_since_round_started", ":hold_time"), #everyone hold
            # (this_or_next|ge, ":agent_group", 0),#player commanded
            # (this_or_next|eq, ":agent_team", ":team_charge"), #start attacker charge
            # (gt, ":seconds_past_since_round_started", 40), #all charge
            (agent_clear_scripted_mode, ":cur_agent"),
          (try_end),
        (try_end),

          (get_max_players, ":num_players"),
          (try_for_range, ":player_no", 1, ":num_players"), #0 is server so starting from 1
            (player_is_active, ":player_no"),
            (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_num_reserves, 1,  "$coop_num_bots_team_1"),
            (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_num_reserves, 2,  "$coop_num_bots_team_2"),
          (try_end),

        ]),


      (ti_on_agent_spawn, 0, 0, [],#called by client also
       [
        (store_trigger_param_1, ":agent_no"),
        (try_begin),
          (eq, "$coop_battle_started", 0),
          (assign, "$coop_battle_started", 1),
        (try_end),
          (try_begin), #add alive team counts for server and client
            (agent_is_human, ":agent_no"),
            (agent_get_team, ":agent_team", ":agent_no"),
            (try_begin),
              (eq, ":agent_team", 0),
              (val_add, "$coop_alive_team1", 1),
            (else_try),
              (eq, ":agent_team", 1),
              (val_add, "$coop_alive_team2", 1),
            (try_end),
          (try_end),


        (try_begin),
          (multiplayer_is_server),
          (try_begin),
            (eq, "$coop_battle_spawn_formation", 1),
            (eq, "$coop_battle_type", coop_battle_type_field_battle), #not for village raids
            (call_script, "script_coop_spawn_formation", ":agent_no"), #move agent to spawn position
          (try_end),


#NEW
          (try_begin),
            (eq, "$coop_battle_type", coop_battle_type_bandit_lair),
            (agent_is_human, ":agent_no"),
            (agent_get_team, ":agent_team", ":agent_no"),
            (eq, ":agent_team", 1),
            (entry_point_get_position, pos30, 0),
            (agent_set_position, ":agent_no", pos30),
          (try_end),

          #check this script for changes, currently only sets multiplayer_ready_for_spawning_agent
          # (call_script, "script_multiplayer_server_on_agent_spawn_common", ":agent_no"),
          (assign, "$g_multiplayer_ready_for_spawning_agent", 1),
          (agent_set_slot, ":agent_no", slot_agent_coop_spawn_party, "$coop_agent_party"), #store party of agent

          (call_script, "script_coop_equip_player_agent", ":agent_no"), #ITEM BUG WORKAROUND
        (try_end),

        (try_begin),
          (agent_is_human, ":agent_no"),
          (agent_get_troop_id,":troop_no", ":agent_no"),

      #common_battle_init_banner 
        (call_script, "script_troop_agent_set_banner", "tableau_game_troop_label_banner", ":agent_no", ":troop_no"),

        #when client's chosen troop spawns, request control of it
          (eq, ":troop_no", "$coop_my_troop_no"),

          (multiplayer_get_my_player, ":my_player_no"),
          (ge, ":my_player_no", 0),
          (player_set_team_no, ":my_player_no", "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_team_no, "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_troop_id, "$coop_my_troop_no"),
        (try_end),

         ]),


      (ti_on_agent_killed_or_wounded, 0, 0, [],
       [
         (store_trigger_param_1, ":dead_agent_no"),
         (store_trigger_param_2, ":killer_agent_no"),
#new
         (call_script, "script_coop_server_on_agent_killed_or_wounded_common", ":dead_agent_no", ":killer_agent_no"),
	       (call_script, "script_multiplayer_server_on_agent_killed_or_wounded_common", ":dead_agent_no", ":killer_agent_no"),
     

         (assign, ":number_of_alive_1", 0),
         (assign, ":number_of_alive_2", 0),
          (try_for_agents, ":cur_agent"),
            (agent_is_human, ":cur_agent"),
            (agent_is_alive, ":cur_agent"),
            (agent_get_team, ":cur_agent_team", ":cur_agent"),
            (try_begin),
              (eq, ":cur_agent_team", 0),
              (val_add, ":number_of_alive_1", 1),
            (else_try),
              (eq, ":cur_agent_team", 1),
              (val_add, ":number_of_alive_2", 1),
            (try_end),
          (try_end),
         (assign, "$coop_alive_team1", ":number_of_alive_1"),
         (assign, "$coop_alive_team2", ":number_of_alive_2"),

        (try_begin), #check round end        
          (this_or_next|eq, ":number_of_alive_1", 0),
          (eq, ":number_of_alive_2", 0),
          (try_begin), #assign my initial team value (only used to set color of multiplayer_message_type_round_result_in_battle_mode)
            (multiplayer_get_my_player, ":my_player_no"),
            (ge, ":my_player_no", 0),
            (player_get_team_no, "$coop_my_team", ":my_player_no"),
            (player_get_team_no, "$my_team_at_start_of_round", ":my_player_no"),
            (player_get_agent_id, ":my_agent_id", ":my_player_no"),
            (ge, ":my_agent_id", 0),
            (agent_get_troop_id, "$coop_my_troop_no", ":my_agent_id"),
          (try_end),     

          (try_begin),
            (eq, "$coop_alive_team1", 0),#if team 1 is dead
            (assign, "$coop_winner_team", 1),
          (else_try),
            (eq, "$coop_alive_team2", 0),#if team 2 is dead
            (assign, "$coop_winner_team", 0),
          (try_end),

          (call_script, "script_show_multiplayer_message", multiplayer_message_type_round_result_in_battle_mode, "$coop_winner_team"), #team 2 is winner 
          (store_mission_timer_a, "$g_round_finish_time"),
          (assign, "$g_round_ended", 1),
        (try_end),


         ]),



#	 END BATTLE ##################	
      (3, 4, ti_once, [(eq, "$g_round_ended", 1)],
       [
        (try_begin),
          (multiplayer_is_server),
          (eq, "$coop_skip_menu", 1),  #do this automatically if skip menu is checked
          (eq, "$coop_battle_started", 1),

          (call_script, "script_coop_copy_parties_to_file_mp"),
          (neg|multiplayer_is_dedicated_server),
          (finish_mission),
        (try_end), 

        ]),


      (ti_tab_pressed, 0, 0, [],
       [
         (try_begin),
           (assign, "$g_multiplayer_stats_chart_opened_manually", 1),
           (start_presentation, "prsnt_coop_stats_chart"),
         (try_end),


         ]),

      (ti_escape_pressed, 0, 0, [],
       [
         (neg|is_presentation_active, "prsnt_coop_escape_menu"),
         (neg|is_presentation_active, "prsnt_coop_stats_chart"),
         (eq, "$g_waiting_for_confirmation_to_terminate", 0),
         (start_presentation, "prsnt_coop_escape_menu"),
         ]),


      ],
  ),



#################  
    (
    "coop_siege",mtf_battle_mode,-1, #siege
    "You lead your men to battle.",
    [
      (0,mtef_visitor_source|mtef_team_1,af_override_horse,aif_start_alarmed,1,[]),
      (1,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (2,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (3,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (4,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (5,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),
      (6,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),
      (7,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),

      (8,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (9,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (10,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),
      (11,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),
      (12,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (13,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (14,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (15,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),

      (16,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (17,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (18,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (19,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (20,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (21,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (22,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (23,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),

      (24,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (25,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (26,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (27,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (28,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (29,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (30,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (31,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),

      (32,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (33,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (34,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (35,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (36,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (37,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (38,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (39,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (40,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (41,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (42,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (43,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (44,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (45,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (46,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (47,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),

      (48,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (49,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (50,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (51,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (52,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (53,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (54,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (55,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (56,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (57,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (58,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (59,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (60,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (61,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (62,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (63,mtef_visitor_source,0,aif_start_alarmed,1,[]),
     ],
    [

      coop_server_check_polls,
      coop_server_reduce_damage,
      coop_respawn_as_bot,
      coop_store_respawn_as_bot,


#mordr does not work in MP = SCRIPT ERROR ON OPCODE 1785: Invalid Group ID: 1;
#      common_battle_order_panel,
#      common_battle_order_panel_tick,


      (ti_server_player_joined, 0, 0, [],
       [
        (store_trigger_param_1, ":player_no"),
       # (call_script, "script_multiplayer_server_player_joined_common", ":player_no"), #dont clear slots

        (call_script, "script_multiplayer_send_initial_information", ":player_no"),
        (call_script, "script_coop_server_player_joined_common", ":player_no"),    #need to call every round
       ]),

      (ti_before_mission_start, 0, 0, [],
       [
         (assign, "$g_multiplayer_game_type", multiplayer_game_type_coop_siege),
     #    (call_script, "script_multiplayer_server_before_mission_start_common"), #dont set time of day, reset commanded troops
     #    (call_script, "script_multiplayer_init_mission_variables"), #dont reset commanded troop type


          (call_script, "script_initialize_banner_info"),
          (call_script, "script_coop_init_mission_variables"),

         (assign, "$g_waiting_for_confirmation_to_terminate", 0),
         (assign, "$g_round_ended", 0),
         (assign, "$coop_winner_team", -1),
         (assign, "$coop_battle_started", 0),
         (assign, "$coop_use_belfry", 0),
         (assign, "$coop_attacker_is_on_wall", 0),
         (call_script, "script_multiplayer_initialize_belfry_wheel_rotations"),

          #set_weather
         (scene_set_day_time, "$coop_time_of_day"),
	       (set_global_cloud_amount, "$coop_cloud"),
	       (set_global_haze_amount, "$coop_haze"),
          #removed set_fog_distance needs correct color in 1.143
         # (try_begin),
           # (gt, "$coop_cloud", 65), #if cloud cover
           # (lt,  "$coop_haze", 91), #not heavy fog
           # (set_global_haze_amount, 95), #remove sunlight
         # (try_end),

         (assign, ":rain_amount", "$coop_cloud"),
         (assign, ":rain_type", "$coop_rain"),
         (try_begin),
           (lt, ":rain_amount", 75), #less than = no rain
           (assign, ":rain_amount", 0),
           (assign, ":rain_type", 0),
         (try_end),
         (set_rain, ":rain_type" , ":rain_amount"), #1=rain 2=snow

#common_battle_mission_start = 
         (try_begin),
           (gt, "$coop_castle_banner", 0),
           (replace_scene_props, banner_scene_props_begin, "$coop_castle_banner"),
         (else_try),
           (replace_scene_props, banner_scene_props_begin, "spr_empty"),
         (try_end),

         ]),

      (ti_after_mission_start, 0, 0, [], 
       [

        (call_script, "script_initialize_all_scene_prop_slots"),
        (call_script, "script_multiplayer_move_moveable_objects_initial_positions"),
        (assign, "$g_multiplayer_bot_type_1_wanted", 1),#set player wants all troops in party (host will override clients)#this should be optional

       #removed set_fog_distance needs correct color in 1.143
         # (try_begin),#limit fog
           # (gt, "$coop_cloud", 65), #if cloud cover
           # (lt,  "$coop_haze", 91), #not heavy fog
           # (try_begin),
             # (eq,  "$coop_rain", 2), #if snow
             # (set_fog_distance, 200), #set fog closer
           # (else_try),
             # (set_fog_distance, 600),
           # (try_end),
         # (try_end),

        (try_begin),
          (neg|multiplayer_is_server),
          #these lines are done in only clients at start of each new round.
          (call_script, "script_multiplayer_initialize_belfry_wheel_rotations"),
          (call_script, "script_initialize_objects_clients"),
        (try_end),  

        (try_begin),
          (multiplayer_is_server),
          (start_presentation, "prsnt_coop_start_battle"),
        (else_try),
          (multiplayer_get_my_player, ":my_player_no"),
          (ge, ":my_player_no", 0),
          (player_is_admin, ":my_player_no"),
          (start_presentation, "prsnt_coop_start_battle"),
        (try_end),

        (try_begin),
          (multiplayer_is_server),
          (assign, "$coop_reinforce_size", 10), #size of reinforcement wave
          (assign, "$coop_reinforce", 1),
          (assign, "$coop_alive_team1", 0),#store count for reinforcement spawn
          (assign, "$coop_alive_team2", 0),



          (entry_point_get_position, pos26, 10),
          (entry_point_get_position, pos31, 0),

          (try_begin),
            (this_or_next|eq, "$coop_round", coop_round_battle),
            (eq, "$coop_round", coop_round_town_street),

            (assign, ":attacker", 0),
            (try_begin),
              (eq, "$coop_round", coop_round_town_street),
              (assign, ":defender", 23),
            (else_try),
              (assign, ":defender", 15),
            (try_end),
 
            (entry_point_get_position, pos2, ":attacker"),
            (entry_point_get_position, pos3, ":defender"),
            (position_set_z_to_ground_level, pos2),
            (position_set_z_to_ground_level, pos3),

            (set_spawn_position, pos2),
            (spawn_scene_prop, "spr_coop_inventory", 0),   
            (try_begin),
              (eq, "$coop_battle_type", coop_battle_type_siege_player_attack),
              (assign, "$coop_inventory_box", reg0),
            (try_end),

            (set_spawn_position, pos3),
            (spawn_scene_prop, "spr_coop_inventory", 0),
            (try_begin),
              (eq, "$coop_battle_type", coop_battle_type_siege_player_defend),
              (assign, "$coop_inventory_box", reg0),
            (try_end),
          (try_end),
        (try_end),


          ]),

      #in later rounds delay so clients can join (can use start battle option to skip)
      (5, 10, ti_once,[
       (multiplayer_is_server),
        (this_or_next|eq, "$coop_round", coop_round_town_street),
        (eq, "$coop_round", coop_round_castle_hall),
        ], 
       [
        (eq, "$coop_battle_started", 0),
        (assign, "$g_multiplayer_ready_for_spawning_agent", 1),
        ]),


#multiplayer_server_spawn_bots
      (0, 0, 0, [], 
       [
        (multiplayer_is_server),
        (eq, "$g_multiplayer_ready_for_spawning_agent", 1),


        #get battle size
        (assign, ":battle_size", "$coop_battle_size"),
        (try_begin), 
          (eq, "$coop_round", coop_round_castle_hall),
          (val_div, ":battle_size", 4),
          (val_max, ":battle_size", coop_min_battle_size),
          (assign, "$coop_reinforce_size",4),
        (try_end),

        #regulate troop spawn
        (store_add, ":total_bots", "$coop_alive_team1", "$coop_alive_team2"),
        (store_sub, ":reinforce_bots", ":battle_size", "$coop_reinforce_size"),#when less troops than battle size
        (try_begin),
          (this_or_next|eq, "$coop_round", coop_round_castle_hall),
          (le, ":total_bots", ":reinforce_bots"), 
          (assign, "$coop_reinforce", 1), #need global var so not cleared
        (try_end),
        (try_begin),
          (ge, ":total_bots", ":battle_size"), 
          (assign, "$coop_reinforce", 0),
        (try_end),


        (try_begin),
          #pick team by size
          (store_add, ":total_req", "$coop_num_bots_team_1", "$coop_num_bots_team_2"),
          (gt, ":total_req", 0),

          (assign, ":alive_team1", "$coop_alive_team1"),
          (assign, ":alive_team2", "$coop_alive_team2"),
          (val_max, ":alive_team1", 1),
          (val_mul, ":alive_team2", 1000),
          (store_div, ":ratio_current", ":alive_team2", ":alive_team1"), 


          (try_begin),
            (this_or_next|eq, "$coop_num_bots_team_2", 0), #skip ratio if other team has no reinforcements
            (ge, ":ratio_current", "$coop_team_ratio"),
            (gt, "$coop_num_bots_team_1", 0),
            (assign, ":selected_team", 0),#add to team 1
          (else_try),
            (gt, "$coop_num_bots_team_2", 0),
            (assign, ":selected_team", 1),#add to team 2
          (try_end),


          #if one team is almost out of troops, choose that team
          (try_begin),
            (le, "$coop_alive_team1", "$coop_reinforce_size"),
            (gt, "$coop_num_bots_team_1", 0),
            (assign, ":selected_team", 0),
          (else_try),
            (le, "$coop_alive_team2", "$coop_reinforce_size"),
            (gt, "$coop_num_bots_team_2", 0),
            (assign, ":selected_team", 1),
          (try_end),

          (try_begin), #server stop reinforcing and be ready for next scene
            (this_or_next|eq, "$coop_round", coop_round_battle),
            (eq, "$coop_round", coop_round_town_street),


            (try_begin),
              (eq, "$defender_team", 0),
              (assign, ":defender_reserves", "$coop_num_bots_team_1"), 
              (assign, ":defender_original_size", "$coop_team_1_troop_num"), 
            (else_try),
              (eq, "$defender_team", 1),
              (assign, ":defender_reserves", "$coop_num_bots_team_2"),
              (assign, ":defender_original_size", "$coop_team_2_troop_num"),  
            (try_end),

            (assign, ":reserves", coop_reserves_hall), #number to reserve for hall battle
            (try_begin),
              (gt, "$coop_street_scene", 0),
              (eq, "$coop_round", coop_round_battle),
              (assign, ":reserves", coop_reserves_street), #if street battle is comming
            (try_end),
            (ge, ":defender_original_size", ":reserves"),
            (le, ":defender_reserves", ":reserves"),
            (val_add, "$coop_round", 1),

          (try_end), 

          #if defenders withdraw, finish spawning attackers
          (try_begin),
            (this_or_next|eq, "$coop_round", coop_round_stop_reinforcing_wall),
            (eq, "$coop_round", coop_round_stop_reinforcing_street),
            (try_begin),
              (eq, "$attacker_team", 0),
              (gt, "$coop_num_bots_team_1", 0),
              (assign, ":selected_team", 0),
            (else_try),
              (eq, "$attacker_team", 1),
              (gt, "$coop_num_bots_team_2", 0),
              (assign, ":selected_team", 1),
            (try_end),

            (try_begin),
              (eq, "$defender_team", 0),
              (eq, "$coop_alive_team1", 0),
              (assign, "$coop_reinforce", 0),
            (else_try),
              (eq, "$defender_team", 1),
              (eq, "$coop_alive_team2", 0),
              (assign, "$coop_reinforce", 0),
            (try_end),
            (eq, "$defender_team", ":selected_team"),
            (assign, "$coop_reinforce", 0),
          (try_end),


          (eq, "$coop_reinforce", 1), #ready for reinforcements
          (call_script, "script_coop_find_bot_troop_for_spawn", ":selected_team"),
          (assign, ":selected_troop", reg0),
#SPAWN POINTS #######################################

          (try_begin),
            (eq, ":selected_team", "$defender_team"),
            (try_begin),#defender spawn points
              (eq, "$coop_round", coop_round_town_street),
              (store_random_in_range, ":random_point", 23, 29),
              (assign, reg0, ":random_point"),
            (else_try),
              (eq, "$coop_round", coop_round_castle_hall),
              (store_random_in_range, ":random_point", 16, 32),
              (assign, reg0, ":random_point"),
            (else_try),
              (assign, reg0, 15), #defenders are moved to other points after spawning
            (try_end),
          (else_try),#attacker spawn point
            (assign, reg0, 0),
          (try_end),
#############################################
          (store_current_scene, ":cur_scene"),
          (modify_visitors_at_site, ":cur_scene"),
          (add_visitors_to_current_scene, reg0, ":selected_troop", 1, ":selected_team", -1),#don't assign group at spawn
          (assign, "$g_multiplayer_ready_for_spawning_agent", 0),

          (try_begin),
            (eq, ":selected_team", 0),
            (val_sub, "$coop_num_bots_team_1", 1),
          (else_try),
            (eq, ":selected_team", 1),
            (val_sub, "$coop_num_bots_team_2", 1),
          (try_end),

        (try_end),   
        ]),
 

      (ti_on_agent_spawn, 0, 0, [],
       [
        (store_trigger_param_1, ":agent_no"),
        (try_begin),
          (eq, "$coop_battle_started", 0),
          (assign, "$coop_battle_started", 1),
        (try_end),

          (try_begin), #add alive team counts for server and client
            (agent_is_human, ":agent_no"),
            (agent_get_team, ":agent_team", ":agent_no"),
            (try_begin),
              (eq, ":agent_team", 0),
              (val_add, "$coop_alive_team1", 1),
            (else_try),
              (eq, ":agent_team", 1),
              (val_add, "$coop_alive_team2", 1),
            (try_end),
          (try_end),

        (try_begin), #move attackers closer to spawn point
          (multiplayer_is_server),
            (agent_is_human, ":agent_no"),
            (agent_get_team, ":agent_team", ":agent_no"),
            (agent_get_class, ":agent_class", ":agent_no"),
        #    (agent_get_troop_id, ":troop_no", ":agent_no"),

            (try_begin),
              (eq, ":agent_team", "$attacker_team"),
              (try_begin),
                (try_begin),
                  (eq, "$coop_round", coop_round_castle_hall),
                  (assign, ":num_row", 2), #2 per row in castle
                (else_try),
                  (eq, "$coop_round", coop_round_town_street),
                  (assign, ":num_row", 4), #4 per row in street
                (else_try),
                  (assign, ":num_row", 20), #20 per row otherwise
                (try_end),
                (val_mul, ":num_row", 50),

                (entry_point_get_position, pos30, 0),
                (get_distance_between_positions, ":dist",pos31,pos30),
                (ge, ":dist", ":num_row"),
                (entry_point_get_position, pos31, 0),
              (try_end),
              # (position_set_z_to_ground_level, pos31),
              (agent_set_position, ":agent_no", pos31),
              (position_move_x, pos31, 50),
            (else_try),
              (eq, ":agent_team", "$defender_team"),
              (eq, "$coop_round", coop_round_battle),

              (try_begin),
          #      (troop_is_guarantee_ranged, ":troop_no"),
                (eq, ":agent_class", grc_archers),
                (store_random_in_range, ":random_point", 40, 47),
                (entry_point_get_position, pos27, ":random_point"),
                 (try_begin),
                  (eq, "$coop_attacker_is_on_wall", 0), 
                  (agent_set_scripted_destination, ":agent_no", pos27, 0), 
                (try_end),
                (try_begin),
                  (eq, "$coop_battle_spawn_formation", 1),#when spawn formation is on, 
                  (position_move_x, pos27, 200),
                  (agent_set_position, ":agent_no", pos27),
                (try_end),

              (else_try),
                (eq, "$coop_attacker_is_on_wall", 0), #before attackers reach wall, move half of defenders to wall
                (entry_point_get_position, pos25, 10),
                (try_begin),
                  # (eq, "$coop_battle_spawn_formation", 1), #when spawn formation is on, 
                  (store_random_in_range, ":random", 0, 2),
                  (eq, ":random", 0),
                  (try_begin),
                    (get_distance_between_positions, ":dist",pos26,pos25),
                    (ge, ":dist", 600), #12 x 50 per row 
                    (entry_point_get_position, pos26, 10),
                  (try_end),
                  (agent_set_position, ":agent_no", pos26),
                  (position_move_x, pos26, 50),
                (try_end),

                (position_move_y, pos25, 100),
                (agent_set_scripted_destination, ":agent_no", pos25, 0),  #keep defenders in castle until attackers reach wall
              (try_end),
            (try_end),

           #check this script for changes, currently only sets g_multiplayer_ready_for_spawning_agent
          # (call_script, "script_multiplayer_server_on_agent_spawn_common", ":agent_no"),
          (assign, "$g_multiplayer_ready_for_spawning_agent", 1),
          (agent_set_slot, ":agent_no", slot_agent_coop_spawn_party, "$coop_agent_party"), #store party of agent
          (call_script, "script_coop_equip_player_agent", ":agent_no"), #ITEM BUG WORKAROUND
        (try_end),
        (agent_set_slot, ":agent_no", slot_agent_coop_banner, "$coop_agent_banner"), #store banner of agent for clients too

        (try_begin),
          (agent_is_human, ":agent_no"),
          (agent_get_troop_id,":troop_no", ":agent_no"),

      #common_battle_init_banner 
        (call_script, "script_troop_agent_set_banner", "tableau_game_troop_label_banner", ":agent_no", ":troop_no"),

        #when client's chosen troop spawns, request control of it
          (eq, ":troop_no", "$coop_my_troop_no"),

          (multiplayer_get_my_player, ":my_player_no"),
          (ge, ":my_player_no", 0),
          # (player_get_team_no, ":my_team_no", ":my_player_no"),
          (agent_get_team, ":agent_team", ":agent_no"),
          (eq, ":agent_team","$coop_my_team"),

          #change team
          (player_set_team_no, ":my_player_no", "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_team_no, "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_troop_id, "$coop_my_troop_no"),
        (try_end),
      

         ]),


      (ti_on_agent_killed_or_wounded, 0, 0, [],
       [
         (store_trigger_param_1, ":dead_agent_no"),
         (store_trigger_param_2, ":killer_agent_no"),
###
         (call_script, "script_coop_server_on_agent_killed_or_wounded_common", ":dead_agent_no", ":killer_agent_no"),
	       (call_script, "script_multiplayer_server_on_agent_killed_or_wounded_common", ":dead_agent_no", ":killer_agent_no"),
     
         (assign, ":number_of_alive_1", 0),
         (assign, ":number_of_alive_2", 0),
          (try_for_agents, ":cur_agent"),
            (agent_is_human, ":cur_agent"),
            (agent_is_alive, ":cur_agent"),
            (agent_get_team, ":cur_agent_team", ":cur_agent"),
            (try_begin),
              (eq, ":cur_agent_team", 0),
              (val_add, ":number_of_alive_1", 1),
            (else_try),
              (eq, ":cur_agent_team", 1),
              (val_add, ":number_of_alive_2", 1),
            (try_end),
          (try_end),
         (assign, "$coop_alive_team1", ":number_of_alive_1"),
         (assign, "$coop_alive_team2", ":number_of_alive_2"),

        (try_begin), #check round end        
          (this_or_next|eq, ":number_of_alive_1", 0),
          (eq, ":number_of_alive_2", 0),
          (try_begin), #assign my initial team value (only used to set color of multiplayer_message_type_round_result_in_battle_mode)
            (multiplayer_get_my_player, ":my_player_no"),
            (ge, ":my_player_no", 0),
            (player_get_team_no, "$coop_my_team", ":my_player_no"),
            (player_get_team_no, "$my_team_at_start_of_round", ":my_player_no"),
            (player_get_agent_id, ":my_agent_id", ":my_player_no"),
            (ge, ":my_agent_id", 0),
            (agent_get_troop_id, "$coop_my_troop_no", ":my_agent_id"),
          (try_end),     

          (try_begin),
            (eq, "$coop_alive_team1", 0),#if team 1 is dead
            (assign, "$coop_winner_team", 1),
            (try_begin),
              (ge, "$coop_num_bots_team_1", coop_reserves_hall), #if loser has reserves, they retreated
              (display_message, "@The defenders retreat!"),
            (try_end),
          (else_try),
            (eq, "$coop_alive_team2", 0),#if team 2 is dead
            (assign, "$coop_winner_team", 0),
            (try_begin),
              (ge, "$coop_num_bots_team_2", coop_reserves_hall), #if loser has reserves, they retreated
              (display_message, "@The defenders retreat!"),
            (try_end),
          (try_end),

          (call_script, "script_show_multiplayer_message", multiplayer_message_type_round_result_in_battle_mode, "$coop_winner_team"), #team 2 is winner 
          (store_mission_timer_a, "$g_round_finish_time"),
          (assign, "$g_round_ended", 1),
        (try_end),
#END BATTLE ##################	
        ]),




#multiplayer_server_check_end_map =                 
      (1, 0, 0,   #must check this in separate trigger in case no defenders spawn in battle round
       [
        (multiplayer_is_server),
        (this_or_next|eq, "$coop_round", coop_round_stop_reinforcing_wall),
        (eq, "$coop_round", coop_round_stop_reinforcing_street),
        ],
       [
        (try_begin),
          (try_begin),
            (eq, "$attacker_team", 0),
            (this_or_next|gt, "$coop_alive_team1", 0), 
            (gt, "$coop_num_bots_team_1", 0),#if attacker is not dead continue
            (eq, "$coop_alive_team2", 0),
            (val_add, "$coop_round", 1),
          (else_try),
            (eq, "$attacker_team", 1),
            (this_or_next|gt, "$coop_alive_team2", 0),
            (gt, "$coop_num_bots_team_2", 0), #if attacker is not dead continue
            (eq, "$coop_alive_team1", 0),
            (val_add, "$coop_round", 1),
          (try_end),

          (this_or_next|eq, "$coop_round", coop_round_town_street),
          (eq, "$coop_round", coop_round_castle_hall),
          (try_begin), 
            (eq, "$coop_street_scene", 0),
            (assign, "$coop_round", coop_round_castle_hall), #if no street scene, skip to castle hall
          (try_end),

          (assign, "$g_multiplayer_ready_for_spawning_agent", 0),

          (try_for_agents, ":cur_agent"),
            (agent_is_human, ":cur_agent"),
            (agent_is_alive, ":cur_agent"),
            (agent_get_team ,":cur_team", ":cur_agent"),
            (agent_get_troop_id, ":agent_troop_id", ":cur_agent"),
            #replace troop in temp spawn party
            (agent_get_slot, ":agent_party",":cur_agent", slot_agent_coop_spawn_party),
            (party_add_members, ":agent_party", ":agent_troop_id", 1),

            (try_begin), #save health for round 2
              (troop_is_hero, ":agent_troop_id"),
              (store_agent_hit_points, ":agent_hit_points", ":cur_agent"),
              (troop_set_health, ":agent_troop_id", ":agent_hit_points"),

              #store items from agents
              (call_script, "script_coop_player_agent_save_items", ":cur_agent"),
            (try_end),

            (try_begin), #replace reserves count
              (eq, ":cur_team", 0),
              (val_add, "$coop_num_bots_team_1", 1),
            (else_try),
              (eq, ":cur_team", 1),
              (val_add, "$coop_num_bots_team_2", 1),
            (try_end),
          (try_end),

          #sort troops of spawn parties
          (store_add, ":last_party", coop_temp_party_enemy_begin, "$coop_no_enemy_parties"), 
          (try_for_range, ":party_no", coop_temp_party_enemy_begin, ":last_party"),
            (call_script, "script_coop_sort_party", ":party_no"),
          (try_end),

          (store_add, ":last_party", coop_temp_party_ally_begin, "$coop_no_ally_parties"), 
          (try_for_range, ":party_no", coop_temp_party_ally_begin, ":last_party"),
            (call_script, "script_coop_sort_party", ":party_no"),
          (try_end),

          (try_begin), 
            (eq, "$coop_round", coop_round_town_street),
            (assign, ":next_scene", "$coop_street_scene"),
          (else_try),
            (eq, "$coop_round", coop_round_castle_hall),
            (assign, ":next_scene", "$coop_castle_scene"),
          (try_end),
          (call_script, "script_game_multiplayer_get_game_type_mission_template", "$g_multiplayer_game_type"),
          (start_multiplayer_mission, reg0, ":next_scene", 1),
        (try_end),
        ]),



#delay after battle to quit
      (3, 4, ti_once, [(eq, "$g_round_ended", 1)],
       [
        (try_begin),
          (multiplayer_is_server),
          (eq, "$coop_skip_menu", 1), #do this automatically if skip menu is checked
          (eq, "$coop_battle_started", 1),
          (store_add, ":total_team1", "$coop_alive_team1", "$coop_num_bots_team_1"), #if one team is defeated
          (store_add, ":total_team2", "$coop_alive_team2", "$coop_num_bots_team_2"),
          (this_or_next|eq, ":total_team1", 0),
          (eq, ":total_team2", 0),

          (call_script, "script_coop_copy_parties_to_file_mp"),
          (neg|multiplayer_is_dedicated_server),
          (finish_mission),
        (try_end), 
        ]),

       
      (ti_tab_pressed, 0, 0, [],
       [
         (try_begin),
           (assign, "$g_multiplayer_stats_chart_opened_manually", 1),
           (start_presentation, "prsnt_coop_stats_chart"),
         (try_end),
         ]),


      (ti_escape_pressed, 0, 0, [],
       [
         (neg|is_presentation_active, "prsnt_coop_escape_menu"),
         (neg|is_presentation_active, "prsnt_coop_stats_chart"),
         (eq, "$g_waiting_for_confirmation_to_terminate", 0),
         (start_presentation, "prsnt_coop_escape_menu"),
         ]),

#multiplayer_server_manage_bots
      (3, 0, 0, [], 
       [
        (multiplayer_is_server),
        (try_for_agents, ":cur_agent"),
          (agent_is_non_player, ":cur_agent"),
          (agent_is_human, ":cur_agent"),
          (agent_is_alive, ":cur_agent"),
          (agent_get_team, ":agent_team", ":cur_agent"),
          (call_script, "script_coop_change_leader_of_bot", ":cur_agent"),

          (try_begin),
            (eq, ":agent_team", "$attacker_team"),
            (eq, "$coop_attacker_is_on_wall", 0),
            (agent_get_position, pos2, ":cur_agent"),
            (entry_point_get_position, pos25, 10),
            (get_distance_between_positions, ":dist",pos2,pos25),
            (lt, ":dist", 500),
            (assign, "$coop_attacker_is_on_wall", 1),
            (display_message, "@The attackers have reached the wall"),
          (try_end),

          (agent_get_group, ":agent_group", ":cur_agent"),
          (try_begin),
            (this_or_next|eq, "$belfry_positioned", 3),#if belfry is positioned
            (eq, "$coop_attacker_is_on_wall", 1),
            (agent_clear_scripted_mode, ":cur_agent"),
          (else_try),
            (this_or_next|eq, "$belfry_positioned", 2),#if belfry is almost positioned
            (ge, ":agent_group", 0),#player commanded
            (eq, ":agent_team", "$attacker_team"),
            (agent_slot_eq,":cur_agent",slot_agent_target_x_pos, 0),
            (agent_clear_scripted_mode, ":cur_agent"),
          (try_end),

#common_siege_attacker_do_not_stall,
          (try_begin),
            (eq, ":agent_team", "$attacker_team"),
            (agent_ai_set_always_attack_in_melee, ":cur_agent", 1),
          (try_end),
        (try_end),

        (get_max_players, ":num_players"),
        (try_for_range, ":player_no", 1, ":num_players"), #0 is server so starting from 1
          (player_is_active, ":player_no"),
          (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_num_reserves, 1,  "$coop_num_bots_team_1"),
          (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_num_reserves, 2,  "$coop_num_bots_team_2"),
        (try_end),

        ]),



#common_siege_refill_ammo = 
      (120, 0, 0, [(multiplayer_is_server)],
      [#refill ammo of defenders every two minutes.
        (try_for_agents,":cur_agent"),
          (agent_is_alive, ":cur_agent"),
          (agent_get_team, ":agent_team", ":cur_agent"),
          (eq, ":agent_team", "$defender_team"),
          (agent_is_non_player, ":cur_agent"),
          (agent_is_human, ":cur_agent"),
          (agent_refill_ammo, ":cur_agent"),
        (try_end),
      ]),



#line up attacking archers (not working) hard to find good position
#      (3, 0, 0,[        
#        (eq, "$coop_round", coop_round_battle),
#        ], 
#        [ 
#        (entry_point_get_position, pos4, 15), #top of ladder
#        (position_move_y, pos4, 5000), 
#        (position_move_x, pos4, -2000), 
#        (call_script, "script_coop_form_line", pos4, "$attacker_team", grc_archers, 200, 100, 3, 0), #(pos, team, dist to row, dist to troop, rows)
#      ]),


#common_siege_init_ai_and_belfry,
      (0, 0, ti_once, [], 
       [
         (try_begin),
           (multiplayer_is_server),
         
           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_a"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_a", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_belfry_platform_moved, 1),
           (try_end),
         
           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_b"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_b", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_belfry_platform_moved, 1),
           (try_end),
          #call coop script
           (call_script, "script_coop_move_belfries_to_their_first_entry_point", "spr_belfry_a"),
           (call_script, "script_coop_move_belfries_to_their_first_entry_point", "spr_belfry_b"),
         
           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_a"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_a", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_number_of_agents_pushing, 0),
             (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_next_entry_point_id, 0),
           (try_end),
         
           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_b"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_b", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_number_of_agents_pushing, 0),
             (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_next_entry_point_id, 0),
           (try_end),

           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_a"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_a", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_belfry_platform_moved, 0),
             (assign, "$coop_use_belfry", 1), #
           (try_end),

           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_b"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_b", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_belfry_platform_moved, 0),
             (assign, "$coop_use_belfry", 1), #
           (try_end),
           (assign, "$belfry_positioned", 0),

         (try_end),
        ]),


#multiplayer_server_check_belfry_movement
      (0, 0, 0, [ ],
       [
    (multiplayer_is_server),
    (eq, "$coop_use_belfry", 1),
    (set_fixed_point_multiplier, 100),

    (try_for_range, ":belfry_kind", 0, 2),
      (try_begin),
        (eq, ":belfry_kind", 0),
        (assign, ":belfry_body_scene_prop", "spr_belfry_a"),
      (else_try),
        (assign, ":belfry_body_scene_prop", "spr_belfry_b"),
      (try_end),
    
      (scene_prop_get_num_instances, ":num_belfries", ":belfry_body_scene_prop"),

      (try_for_range, ":belfry_no", 0, ":num_belfries"),
        (scene_prop_get_instance, ":belfry_scene_prop_id", ":belfry_body_scene_prop", ":belfry_no"),
        (prop_instance_get_position, pos1, ":belfry_scene_prop_id"), #pos1 holds position of current belfry 
        (prop_instance_get_starting_position, pos11, ":belfry_scene_prop_id"),

#common_siege_assign_men_to_belfry = 
        (call_script, "script_cf_coop_siege_assign_men_to_belfry",  pos1),

#        (store_add, ":belfry_first_entry_point_id", 11, ":belfry_no"), #belfry entry points are 110..119 and 120..129 and 130..139
        (store_add, ":belfry_first_entry_point_id", 5, ":belfry_no"), #belfry entry points are 50..55 and 60..65 and 70..75
        (try_begin),
          (eq, ":belfry_kind", 1),
          (scene_prop_get_num_instances, ":number_of_belfry_a", "spr_belfry_a"),
          (val_add, ":belfry_first_entry_point_id", ":number_of_belfry_a"),
        (try_end),        
                
        (val_mul, ":belfry_first_entry_point_id", 10),
#        (store_add, ":belfry_last_entry_point_id", ":belfry_first_entry_point_id", 10),#number points for each belfry
        (store_add, ":belfry_last_entry_point_id", ":belfry_first_entry_point_id", 5),#number points for each belfry
    
        (try_for_range, ":entry_point_id", ":belfry_first_entry_point_id", ":belfry_last_entry_point_id"),
          (entry_point_is_auto_generated, ":entry_point_id"),
          (assign, ":belfry_last_entry_point_id", ":entry_point_id"),
        (try_end),
        
        (assign, ":belfry_last_entry_point_id_plus_one", ":belfry_last_entry_point_id"),
        (val_sub, ":belfry_last_entry_point_id", 1),
        (assign, reg0, ":belfry_last_entry_point_id"),
        (neg|entry_point_is_auto_generated, ":belfry_last_entry_point_id"),

        (try_begin),
          (get_sq_distance_between_positions, ":dist_between_belfry_and_its_destination", pos1, pos11),

          (ge, ":dist_between_belfry_and_its_destination", 4), #0.2 * 0.2 * 100 = 4 (if distance between belfry and its destination already less than 20cm no need to move it anymore)

          # coop check when belfry is close
          (try_begin),
            (lt, ":dist_between_belfry_and_its_destination", 1000),
            (assign, "$belfry_positioned", 2), 
          (try_end),

          (try_begin),
            (lt, "$belfry_positioned", 2), 
            (copy_position, pos4, pos1),
            (position_move_y, pos4, -2400),
            (position_move_x, pos4, -800),
            (call_script, "script_coop_form_line", pos4, "$attacker_team", grc_everyone, 200, 100, 3, 0), #(pos, team, dist to row, dist to troop, rows)
          (try_end),


          (assign, ":max_dist_between_entry_point_and_belfry_destination", -1), #should be lower than 0 to allow belfry to go last entry point
          (assign, ":belfry_next_entry_point_id", -1),
          (try_for_range, ":entry_point_id", ":belfry_first_entry_point_id", ":belfry_last_entry_point_id_plus_one"),
            (entry_point_get_position, pos4, ":entry_point_id"),
            (get_sq_distance_between_positions, ":dist_between_entry_point_and_belfry_destination", pos11, pos4),
            (lt, ":dist_between_entry_point_and_belfry_destination", ":dist_between_belfry_and_its_destination"),
            (gt, ":dist_between_entry_point_and_belfry_destination", ":max_dist_between_entry_point_and_belfry_destination"),
            (assign, ":max_dist_between_entry_point_and_belfry_destination", ":dist_between_entry_point_and_belfry_destination"),
            (assign, ":belfry_next_entry_point_id", ":entry_point_id"),
          (try_end),

          (try_begin),
            (ge, ":belfry_next_entry_point_id", 0),
            (entry_point_get_position, pos5, ":belfry_next_entry_point_id"), #pos5 holds belfry next entry point target during its path
          (else_try),
            (copy_position, pos5, pos11),    
          (try_end),
        
          (get_distance_between_positions, ":belfry_next_entry_point_distance", pos1, pos5),
        
          #collecting scene prop ids of belfry parts
          (try_begin),
            (eq, ":belfry_kind", 0),
            #belfry platform_a
            (scene_prop_get_instance, ":belfry_platform_a_scene_prop_id", "spr_belfry_platform_a", ":belfry_no"),
            #belfry platform_b
            (scene_prop_get_instance, ":belfry_platform_b_scene_prop_id", "spr_belfry_platform_b", ":belfry_no"),
          (else_try),
            #belfry platform_a
            (scene_prop_get_instance, ":belfry_platform_a_scene_prop_id", "spr_belfry_b_platform_a", ":belfry_no"),
          (try_end),
    
          #belfry wheel_1
          (store_mul, ":wheel_no", ":belfry_no", 3),
          (try_begin),
            (eq, ":belfry_body_scene_prop", "spr_belfry_b"),
            (scene_prop_get_num_instances, ":number_of_belfry_a", "spr_belfry_a"),    
            (store_mul, ":number_of_belfry_a_wheels", ":number_of_belfry_a", 3),
            (val_add, ":wheel_no", ":number_of_belfry_a_wheels"),
          (try_end),
          (scene_prop_get_instance, ":belfry_wheel_1_scene_prop_id", "spr_belfry_wheel", ":wheel_no"),
          #belfry wheel_2
          (val_add, ":wheel_no", 1),
          (scene_prop_get_instance, ":belfry_wheel_2_scene_prop_id", "spr_belfry_wheel", ":wheel_no"),
          #belfry wheel_3
          (val_add, ":wheel_no", 1),
          (scene_prop_get_instance, ":belfry_wheel_3_scene_prop_id", "spr_belfry_wheel", ":wheel_no"),

          (init_position, pos17),
          (position_move_y, pos17, -225),
          (position_transform_position_to_parent, pos18, pos1, pos17),
          (position_move_y, pos17, -225),
          (position_transform_position_to_parent, pos19, pos1, pos17),

          (assign, ":number_of_agents_around_belfry", 0),
#
#          (get_max_players, ":num_players"),
#          (try_for_range, ":player_no", 0, ":num_players"),
#            (player_is_active, ":player_no"),
#            (player_get_agent_id, ":agent_id", ":player_no"),
#            (ge, ":agent_id", 0),
          (try_for_agents, ":agent_id"),
            (agent_is_human, ":agent_id"),
            (agent_is_alive, ":agent_id"),

            (agent_get_team, ":agent_team", ":agent_id"),
            (eq, ":agent_team", "$attacker_team"),
 
            (agent_get_position, pos2, ":agent_id"),
            (get_sq_distance_between_positions_in_meters, ":dist_between_agent_and_belfry", pos18, pos2),

#            (lt, ":dist_between_agent_and_belfry", multi_distance_sq_to_use_belfry), #must be at most 10m * 10m = 100m away from the player
            (lt, ":dist_between_agent_and_belfry", 140), #must be at most 10m * 10m = 100m away from the player
            (neg|scene_prop_has_agent_on_it, ":belfry_scene_prop_id", ":agent_id"),
            (neg|scene_prop_has_agent_on_it, ":belfry_platform_a_scene_prop_id", ":agent_id"),

            (this_or_next|eq, ":belfry_kind", 1), #there is this_or_next here because belfry_b has no platform_b
            (neg|scene_prop_has_agent_on_it, ":belfry_platform_b_scene_prop_id", ":agent_id"),
    
            (neg|scene_prop_has_agent_on_it, ":belfry_wheel_1_scene_prop_id", ":agent_id"),#can be removed to make faster
            (neg|scene_prop_has_agent_on_it, ":belfry_wheel_2_scene_prop_id", ":agent_id"),#can be removed to make faster
            (neg|scene_prop_has_agent_on_it, ":belfry_wheel_3_scene_prop_id", ":agent_id"),#can be removed to make faster
            (neg|position_is_behind_position, pos2, pos19),
            (position_is_behind_position, pos2, pos1),
            (val_add, ":number_of_agents_around_belfry", 1),        
          (try_end),

          (val_min, ":number_of_agents_around_belfry", 16),

          (try_begin),
            (scene_prop_get_slot, ":pre_number_of_agents_around_belfry", ":belfry_scene_prop_id", scene_prop_number_of_agents_pushing),
            (scene_prop_get_slot, ":next_entry_point_id", ":belfry_scene_prop_id", scene_prop_next_entry_point_id),
            (this_or_next|neq, ":pre_number_of_agents_around_belfry", ":number_of_agents_around_belfry"),
            (neq, ":next_entry_point_id", ":belfry_next_entry_point_id"),

            (try_begin),
              (eq, ":next_entry_point_id", ":belfry_next_entry_point_id"), #if we are still targetting same entry point subtract 
              (prop_instance_is_animating, ":is_animating", ":belfry_scene_prop_id"),
              (eq, ":is_animating", 1),

              (store_mul, ":sqrt_number_of_agents_around_belfry", "$g_last_number_of_agents_around_belfry", 100),
              (store_sqrt, ":sqrt_number_of_agents_around_belfry", ":sqrt_number_of_agents_around_belfry"),
              (val_min, ":sqrt_number_of_agents_around_belfry", 300),
              (assign, ":distance", ":belfry_next_entry_point_distance"),
              (val_mul, ":distance", ":sqrt_number_of_agents_around_belfry"),
              (val_div, ":distance", 100), #100 is because of fixed_point_multiplier
              (val_mul, ":distance", 8), #multiplying with 4 to make belfry pushing process slower, 
                                                                 #with 16 agents belfry will go with 4 / 4 = 1 speed (max), with 1 agent belfry will go with 1 / 4 = 0.25 speed (min)    
            (try_end),

            (try_begin),
              (ge, ":belfry_next_entry_point_id", 0),

              #up down rotation of belfry's next entry point
              (init_position, pos9),
              (position_set_y, pos9, -500), #go 5.0 meters back
              (position_set_x, pos9, -300), #go 3.0 meters left
              (position_transform_position_to_parent, pos10, pos5, pos9), 
              (position_get_distance_to_terrain, ":height_to_terrain_1", pos10), #learn distance between 5 meters back of entry point(pos10) and ground level at left part of belfry
      
              (init_position, pos9),
              (position_set_y, pos9, -500), #go 5.0 meters back
              (position_set_x, pos9, 300), #go 3.0 meters right
              (position_transform_position_to_parent, pos10, pos5, pos9), 
              (position_get_distance_to_terrain, ":height_to_terrain_2", pos10), #learn distance between 5 meters back of entry point(pos10) and ground level at right part of belfry

              (store_add, ":height_to_terrain", ":height_to_terrain_1", ":height_to_terrain_2"),
              (val_mul, ":height_to_terrain", 100), #because of fixed point multiplier

              (store_div, ":rotate_angle_of_next_entry_point", ":height_to_terrain", 24), #if there is 1 meters of distance (100cm) then next target position will rotate by 2 degrees. #ac sonra
              (init_position, pos20),    
              (position_rotate_x_floating, pos20, ":rotate_angle_of_next_entry_point"),
              (position_transform_position_to_parent, pos23, pos5, pos20),

              #right left rotation of belfry's next entry point
              (init_position, pos9),
              (position_set_x, pos9, -300), #go 3.0 meters left
              (position_transform_position_to_parent, pos10, pos5, pos9), #applying 3.0 meters in -x to position of next entry point target, final result is in pos10
              (position_get_distance_to_terrain, ":height_to_terrain_at_left", pos10), #learn distance between 3.0 meters left of entry point(pos10) and ground level
              (init_position, pos9),
              (position_set_x, pos9, 300), #go 3.0 meters left
              (position_transform_position_to_parent, pos10, pos5, pos9), #applying 3.0 meters in x to position of next entry point target, final result is in pos10
              (position_get_distance_to_terrain, ":height_to_terrain_at_right", pos10), #learn distance between 3.0 meters right of entry point(pos10) and ground level
              (store_sub, ":height_to_terrain_1", ":height_to_terrain_at_left", ":height_to_terrain_at_right"),

              (init_position, pos9),
              (position_set_x, pos9, -300), #go 3.0 meters left
              (position_set_y, pos9, -500), #go 5.0 meters forward
              (position_transform_position_to_parent, pos10, pos5, pos9), #applying 3.0 meters in -x to position of next entry point target, final result is in pos10
              (position_get_distance_to_terrain, ":height_to_terrain_at_left", pos10), #learn distance between 3.0 meters left of entry point(pos10) and ground level
              (init_position, pos9),
              (position_set_x, pos9, 300), #go 3.0 meters left
              (position_set_y, pos9, -500), #go 5.0 meters forward
              (position_transform_position_to_parent, pos10, pos5, pos9), #applying 3.0 meters in x to position of next entry point target, final result is in pos10
              (position_get_distance_to_terrain, ":height_to_terrain_at_right", pos10), #learn distance between 3.0 meters right of entry point(pos10) and ground level
              (store_sub, ":height_to_terrain_2", ":height_to_terrain_at_left", ":height_to_terrain_at_right"),

              (store_add, ":height_to_terrain", ":height_to_terrain_1", ":height_to_terrain_2"),    
              (val_mul, ":height_to_terrain", 100), #100 is because of fixed_point_multiplier
              (store_div, ":rotate_angle_of_next_entry_point", ":height_to_terrain", 24), #if there is 1 meters of distance (100cm) then next target position will rotate by 25 degrees. 
              (val_mul, ":rotate_angle_of_next_entry_point", -1),

              (init_position, pos20),
              (position_rotate_y_floating, pos20, ":rotate_angle_of_next_entry_point"),
              (position_transform_position_to_parent, pos22, pos23, pos20),
            (else_try),
              (copy_position, pos22, pos5),      
            (try_end),
              
            (try_begin),
              (ge, ":number_of_agents_around_belfry", 1), #if there is any agents pushing belfry

              (store_mul, ":sqrt_number_of_agents_around_belfry", ":number_of_agents_around_belfry", 100),
              (store_sqrt, ":sqrt_number_of_agents_around_belfry", ":sqrt_number_of_agents_around_belfry"),
              (val_min, ":sqrt_number_of_agents_around_belfry", 300),
              (val_mul, ":belfry_next_entry_point_distance", 100), #100 is because of fixed_point_multiplier
              (val_mul, ":belfry_next_entry_point_distance", 8), #multiplying with 3 to make belfry pushing process slower, 
                                                                 #with 9 agents belfry will go with 3 / 3 = 1 speed (max), with 1 agent belfry will go with 1 / 3 = 0.33 speed (min)    
              (val_div, ":belfry_next_entry_point_distance", ":sqrt_number_of_agents_around_belfry"),
              #calculating destination coordinates of belfry parts
              #belfry platform_a
              (prop_instance_get_position, pos6, ":belfry_platform_a_scene_prop_id"),
              (position_transform_position_to_local, pos7, pos1, pos6),
              (position_transform_position_to_parent, pos8, pos22, pos7),
              (prop_instance_animate_to_position, ":belfry_platform_a_scene_prop_id", pos8, ":belfry_next_entry_point_distance"),    
              #belfry platform_b
              (try_begin),
                (eq, ":belfry_kind", 0),
                (prop_instance_get_position, pos6, ":belfry_platform_b_scene_prop_id"),
                (position_transform_position_to_local, pos7, pos1, pos6),
                (position_transform_position_to_parent, pos8, pos22, pos7),
                (prop_instance_animate_to_position, ":belfry_platform_b_scene_prop_id", pos8, ":belfry_next_entry_point_distance"),
              (try_end),
              #wheel rotation
              (store_mul, ":belfry_wheel_rotation", ":belfry_next_entry_point_distance", 25), #-25 fixed bug rotation was reversed
              #(val_add, "$g_belfry_wheel_rotation", ":belfry_wheel_rotation"),
              (assign, "$g_last_number_of_agents_around_belfry", ":number_of_agents_around_belfry"),

              #belfry wheel_1
              #(prop_instance_get_starting_position, pos13, ":belfry_wheel_1_scene_prop_id"),
              (prop_instance_get_position, pos13, ":belfry_wheel_1_scene_prop_id"),
              (prop_instance_get_position, pos20, ":belfry_scene_prop_id"),
              (position_transform_position_to_local, pos7, pos20, pos13),
              (position_transform_position_to_parent, pos21, pos22, pos7),
              (prop_instance_rotate_to_position, ":belfry_wheel_1_scene_prop_id", pos21, ":belfry_next_entry_point_distance", ":belfry_wheel_rotation"),
      
              #belfry wheel_2
              #(prop_instance_get_starting_position, pos13, ":belfry_wheel_2_scene_prop_id"),
              (prop_instance_get_position, pos13, ":belfry_wheel_2_scene_prop_id"),
              (prop_instance_get_position, pos20, ":belfry_scene_prop_id"),
              (position_transform_position_to_local, pos7, pos20, pos13),
              (position_transform_position_to_parent, pos21, pos22, pos7),
              (prop_instance_rotate_to_position, ":belfry_wheel_2_scene_prop_id", pos21, ":belfry_next_entry_point_distance", ":belfry_wheel_rotation"),
      
              #belfry wheel_3
              (prop_instance_get_position, pos13, ":belfry_wheel_3_scene_prop_id"),
              (prop_instance_get_position, pos20, ":belfry_scene_prop_id"),
              (position_transform_position_to_local, pos7, pos20, pos13),
              (position_transform_position_to_parent, pos21, pos22, pos7),
              (prop_instance_rotate_to_position, ":belfry_wheel_3_scene_prop_id", pos21, ":belfry_next_entry_point_distance", ":belfry_wheel_rotation"),

              #belfry main body
              (prop_instance_animate_to_position, ":belfry_scene_prop_id", pos22, ":belfry_next_entry_point_distance"),    
            (else_try),
              (prop_instance_is_animating, ":is_animating", ":belfry_scene_prop_id"),
              (eq, ":is_animating", 1),

              #belfry platform_a
              (prop_instance_stop_animating, ":belfry_platform_a_scene_prop_id"),
              #belfry platform_b
              (try_begin),
                (eq, ":belfry_kind", 0),
                (prop_instance_stop_animating, ":belfry_platform_b_scene_prop_id"),
              (try_end),
              #belfry wheel_1
              (prop_instance_stop_animating, ":belfry_wheel_1_scene_prop_id"),
              #belfry wheel_2
              (prop_instance_stop_animating, ":belfry_wheel_2_scene_prop_id"),
              #belfry wheel_3
              (prop_instance_stop_animating, ":belfry_wheel_3_scene_prop_id"),
              #belfry main body
              (prop_instance_stop_animating, ":belfry_scene_prop_id"),
            (try_end),
        
            (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_number_of_agents_pushing, ":number_of_agents_around_belfry"),    
            (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_next_entry_point_id, ":belfry_next_entry_point_id"),
          (try_end),
        (else_try),
          (le, ":dist_between_belfry_and_its_destination", 4),
          (scene_prop_slot_eq, ":belfry_scene_prop_id", scene_prop_belfry_platform_moved, 0),
      
          (scene_prop_set_slot, ":belfry_scene_prop_id", scene_prop_belfry_platform_moved, 1),    

          (try_begin),
            (eq, ":belfry_kind", 0),
            (scene_prop_get_instance, ":belfry_platform_a_scene_prop_id", "spr_belfry_platform_a", ":belfry_no"),
          (else_try),
            (scene_prop_get_instance, ":belfry_platform_a_scene_prop_id", "spr_belfry_b_platform_a", ":belfry_no"),
          (try_end),
          (assign, "$belfry_positioned", 3),   #
          (prop_instance_get_starting_position, pos0, ":belfry_platform_a_scene_prop_id"),
          (prop_instance_animate_to_position, ":belfry_platform_a_scene_prop_id", pos0, 1000),  #400

        (try_end),
      (try_end),
    (try_end),
    ]),

    ],
  ),

]
