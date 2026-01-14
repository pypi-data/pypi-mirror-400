from typing import Literal


class SHAPEID:
    """Shape ID constants for Blocks and Parts.
    """
    Steel_Pallet = '007d6afc-59ef-4fb4-9bb7-52ab9bcfec22'
    Duct_Long = '01d2298b-6cdb-4f4f-bd73-37c76cd60ca3'
    Mountable_Spud_Gun = '454ad69d-bac2-4b06-9386-6267bcbfece2'
    Valve = '04782466-eca1-4ed9-8502-036ea269aed9'
    Wires_Long = '0535b90e-f0a8-491c-8c70-1fc81b939fb4'
    Stop_Sign = '068a89ca-504e-4782-9ede-48f710aeea73'
    Pipe_Long = '07232236-22eb-4912-8774-ab185f368bb9'
    Large_Pipe_Join = '08918d4d-29e6-427d-ad8c-1eafcc4af1f9'
    Ventilation_Grid = '0a597f6d-eb45-4f93-91e5-130e19e0f1f5'
    Small_Pipe_Short = '0dba257b-b907-4919-baaf-2fefe19f4e24'
    Open_Plant_Container = '102565a0-c864-463e-b517-72e82242eec2'
    Controller = '12862001-666c-4bdd-8326-a1f43610d28b'
    Woc_Capsule = '12cc6e9a-6d66-4a9a-bb59-b13a50373fd8'
    Air_Conditioner = '1325d152-3dd1-41a1-9027-5823c5cb55c4'
    Grass_Container = '13ffabca-91ec-48ce-9dd6-4f6660714701'
    Beware_Farmbots_Sign = '14e8f5d0-7d6a-41ab-96a1-fc34588de868'
    Large_Support_Structure = '15a8f24b-016a-4db6-adcc-967ee1b6c7b1'
    Totebot_Head_Bass = '161786c1-1290-4817-8f8b-7f80de755a06'
    Large_Pipe_Corner = '17153a0e-8461-442f-b172-3a899c1ae99f'
    Banana_Box = '18a38c8e-18ec-46c5-be00-cee7724401e2'
    Exit_Sign = '1a82f776-5989-4471-b09d-0c3f65012fb3'
    Totebot_Head_Blip = '1c04327f-1de4-4b06-92a8-2c9b40e491aa'
    Satellite_Dish = '1daf2b8a-fd2f-4266-9942-c04feede4f7b'
    Button = '1e8d93a4-506b-470d-9ada-9c0a321e2db5'
    I_Beam_Holder = '1ed1d5a8-466a-4b5e-867b-0d93cd9d2dcb'
    Staircase_Baluster = '1ef1f0e8-389c-4eb9-b4a8-784499353f14'
    Traffic_Cone = '1f334b62-8955-4406-8848-91e03228c330'
    Small_Pipe_Corner = '203fdf06-b311-49fd-933d-a1c6b671a017'
    Saddle = '20f59114-5964-451f-bb47-820da3ebbc3b'
    Large_Explosive_Canister = '24001201-40dd-4950-b99f-17d878a9e07b'
    Staircase_Railing_Join = '295451dd-f5b2-421d-9113-b3f704d799d4'
    Small_Support_Structure = '29ededf7-6436-41bf-84f4-8fb5361d29ea'
    Tubes_Long = '2ba72fca-443a-49e4-8eb2-073c4226866e'
    Skull_Sign = '2ccaa006-008e-4069-8de1-15668050f92e'
    I_Beam_Corner = '31768765-5a08-499a-a7e6-7e7613363f75'
    Wires_Bend = '33102836-a94d-4ab3-9864-3d54d32c230d'
    Support_Structure = '33d5f0c1-f80c-478a-b69d-9edafe376474'
    Green_Totebot_Capsule = '34d22fc5-0a45-4d71-9aaf-64df1355c272'
    Small_Pipe_Four_Way = '387095d6-5aba-45e3-abd0-098710c268f8'
    Arrow_Sign = '3878d965-de4a-4e7b-a15a-73cc032158b6'
    Drivers_Saddle = '38ee0516-abc5-4e46-9195-c763610d7ec4'
    Bathtub = '3efe715f-8745-475f-a609-5e7cbe09a8ef'
    Sink = '3fa0afca-7715-459e-86fa-2a81cf3027b8'
    Raft_Shark_Mount = '4152ce33-9b43-4c51-80a3-e0b4fe38841d'
    Seat = '42786777-c148-4e13-9bab-e460564e79c3'
    Support_Pillar_Stand = '45e5c193-8896-4687-a4b0-cf4b2da047d1'
    Bearing = '4a1b886b-913e-4aad-b5b6-6e41b0db23a6'
    Tapebot_Capsule = '4c5c3ffd-9aaf-4ded-a7c5-452d239cac32'
    Totebot_Head_Percussion = '4c6e27a2-4c35-4df3-9794-5e206fef9012'
    Long_I_Beam = '4c7b8096-b8ca-4341-bfe9-d31d2d5443b8'
    Pipe_Corner = '4f1c0036-389b-432e-81de-8261cb9f9d57'
    Small_Windshield = '50007ac9-e97d-4b32-9fd6-de919c8a34a4'
    Red_Tapebot_Capsule = '50f624e6-7e33-4118-8252-2219e73e9af1'
    Square_Window = '53349c8d-14e8-4055-bd79-a1ab56fe876e'
    Large_Pipe_Long = '53e8478f-517f-4ea0-be9c-f4a357400cc1'
    U_Beam = '56545d5c-556d-4cd5-9125-6e34acf37c3d'
    Small_Rectangular_Window = '57fad8e9-2aff-40c3-9d5c-8f81573b58b9'
    Small_Pipe_Four_Way_Tee = '5a106512-9284-40de-be68-2c186e903097'
    Thruster = '5e96037a-a338-490a-a76f-6b4d820f8e46'
    Staircase_Ramp = '635eee58-9a36-437f-9e30-78dab0cbcc59'
    Tubes_Short = '647296c4-41ef-4173-8a54-d2a1ae1e89c3'
    Electric_Engine = '6546c293-a5aa-4442-80d5-a2819f077746'
    Large_Tank = '68c2baa5-1274-4bfd-8b12-6e522123f4de'
    Warehouse_Spotlight = '16ba2d22-7b96-4c5e-9eb7-f6422ed80ad4'
    Fuse_Box = '697e3b80-d3f7-4f4a-aba2-23611a45f967'
    Wheel = '69e362c3-32aa-4cd1-adc0-dcfc47b92c0d'
    Table_Support = '6a720005-ba27-4cfc-8fb3-b1af8b9c8bd3'
    Metal_Column = '6b78fb4b-2af9-4a01-a7c5-7e333d245adb'
    Wires_Short = '6be64f78-927b-4f61-b645-20adfbd9bfce'
    Duct_Join = '6f0c29d3-f8c1-4314-b13d-db637ed89061'
    Construction_Zone_Sign = '70bf77d0-c9dd-4232-9e05-fbf7f49bd62c'
    Large_Rectangular_Window = '763fd838-7ed5-420e-8984-c2ae86da1e5c'
    Glowbug_Capsule = '7735cab3-56d7-4d52-b615-090d021e8fdc'
    Big_Pot = '7826f497-426b-42cb-a857-0d784f3ab2f3'
    Large_Windshield = '7a0e9041-9dd5-4cb1-b804-69ee16c45efe'
    Switch = '7cf717d7-d167-4f2d-a6e7-6b2c70aa3986'
    Beetroot_Box = '7ece2c9b-bc74-45b7-b5f1-4c6f41a03a7a'
    Small_Pipe_Bend = '8024db09-9147-4fe3-a747-00bc30ab724b'
    Vegetable_Box = '80550b05-f9eb-433c-9773-2af3beb1479d'
    Baby_Duck_Statuette = '80bc2b9f-98a9-44e4-9cb8-d4ec7e95b40f'
    Horn = '818f4e15-ff51-4fed-b874-723a25d62e1c'
    Staircase_Short_Railing = '8336bf8b-cde0-46a0-b995-5000cba4f27f'
    Staircase_Long_Railing = '85379fe5-da83-4aa2-b9c2-d67476ad6079'
    Large_Pipe_Short = '862f6857-3050-4a84-8191-6a7cbb50bd1a'
    Short_I_Beam = '87878e83-8170-4796-9401-6baba45ccef2'
    Tubes_Join = '885ab381-007d-4a60-99e3-c58dec54c880'
    Small_Potted_Plant = '89f6c762-c0ed-44ad-b3f1-a60dbdd889c5'
    Fruit_Box = '8b684022-254b-41af-a58c-ec4b14791000'
    Orange_Box = '8bcc5a38-b566-45fe-b47e-45118ee70d2d'
    Metal_Window = '8c4b9721-3de4-4ae3-a7d1-6f66a16d1368'
    Small_Explosive_Canister = '8d3b98de-c981-4f05-abfe-d22ee4781d33'
    Shelf_Support = '8d7be7bf-37c9-44d6-8adf-fc87b141cadf'
    Timer = '8f7fd0e7-c46e-4944-a414-7ce2437bb30f'
    Tubes_Corner = '903b0823-4ce1-48e6-9702-aeaa7598c347'
    Small_Pipe_Long = '927d80d8-84ee-44f0-9d8b-cb7a688e0b6c'
    Caution_Sign = '99b7fd1d-7126-4928-bfc2-f82befcbd905'
    Farmbot_Capsule = '9c1f1f76-7391-4661-ae32-e96250030229'
    Small_Pipe_Six_Way = '9c6d8dba-1783-4c42-8a02-6af1c5d63ec6'
    Duct_Short = '9d7e182f-c5d6-45e9-af21-1c24977b30c9'
    Mattress = '9eead4cf-4743-486e-99be-a553c4c10740'
    Logic_Gate = '9f0f56e8-2c31-4d83-996c-d00a9b296c3f'
    Pipe_Join = '9f37d9e9-be8d-49c8-a7ac-e59c67786083'
    Totebot_Head_Synth_Voice = 'a052e116-f273-4d73-872c-924a97b86720'
    Danger_Sign = 'a5198434-2639-4cb0-8e01-865bc4d9b791'
    Mug = 'a6ec1dcc-07e9-418a-819e-904e28a32f63'
    Wires_Concave_Bend = 'a8164438-65fa-4840-8bc2-766fad543841'
    Support_Pillar = 'aa5325da-03f9-46cc-9655-983ee7ac2ab2'
    Sensor = 'add3acc6-a6fd-44e8-a384-a7a16ce13c81'
    Maintenance_Ship_Door = 'aec1ff30-9347-4166-9cb7-f414e1563d9d'
    Duct_Holder = 'b050533f-200b-4253-9532-c2cfa273f982'
    Mannequin_Hand = 'b1dd7967-da2a-4ff5-a90f-bbd7e9bae4d7'
    Do_Not_Enter_Sign = 'b4498227-6650-4e52-b5a6-6db7a7b34d14'
    Staircase_Banister = 'b50a014c-0785-4b1b-b63e-51cfdb7e49ad'
    I_Beam_End = 'b9775316-7272-4a66-a8a9-179108d76f18'
    Potted_Blue_Flower = 'bb443a05-b5b9-4fad-90fc-5e04aa90fd8f'
    Pipe_Short = 'bbc5cc77-443d-4aa7-a175-ebdeb09c2df3'
    Potted_Cactus = 'bc575e0c-d1aa-438e-9f3d-0a80f4ea915f'
    Wooden_Crate = 'c3990931-b471-4e89-beb5-0baaef47f0af'
    Metal_Support = 'c40683f3-d9ce-4067-af24-3514c1867a1a'
    Potted_Seed_Plant = 'c4609540-bc32-4c3f-83b8-3b6926878012'
    Screw = 'c5e56da5-bc3f-4519-91c2-b307d36e15aa'
    Small_Pipe_Five_Way = 'c6ebae46-8e69-4ddd-a3c0-895d887027bd'
    Falling_Objects_Sign = 'c79a1857-a5c7-4616-b507-f1b151c31fe8'
    Mannequin_Boot = 'c89f7bc8-5720-474d-989d-761916a411b2'
    Shelf = 'c8c07259-bc23-45a1-8a4c-585962274f19'
    Reflector_Antenna = 'c938e84c-ff59-4e7e-a87c-5211ac903927'
    Toilet = 'ca003562-fde7-463c-969e-f8334ae54387'
    Satellite_Reflector_Dish = 'ce350b5c-cebb-42b0-b8ba-1bf084a0090c'
    Potted_Vine_Plant = 'cec1d36c-b48a-43d2-9667-5e53b62dd4c5'
    Drivers_Seat = 'cf3fdcfc-a7e5-4497-b000-ffda67dd8db7'
    Potted_Blooming_Cactus = 'd1421af8-6f80-4413-8099-2c6b217fb929'
    Welcome_Sign = 'd509a432-85f9-419f-8b02-8d58b1082f97'
    Staircase_Landing = 'd5da6d42-69e2-49ca-8def-3339bf9f0d35'
    Gas_Engine = 'd5e36413-b3c1-4636-8447-3410c352ec7b'
    Medium_Tank = 'd71d8897-5af6-4adc-b626-50e45f931157'
    Duct_Corner = 'd97a85c5-7c0f-4bfb-9ef4-ce6ecdab9539'
    Haybot_Capsule = 'da993c70-ba90-4748-8a22-6246bad32930'
    Big_Wheel = 'db66f0b1-0c50-4b74-bdc7-771374204b1f'
    Shelf_Pillar = 'dbd509b5-b7cc-43cf-9a89-b3befecfe991'
    Onion_Box = 'de467c9b-a0ab-4e20-95ae-0e5fe8140989'
    Potted_Plant = 'df3734e2-f04b-443f-b568-fe5b076646c7'
    Radio = 'dfefc9d7-db03-4d25-ad85-eae1d824d8c0'
    Staircase_Wedge = 'e02620a5-371b-4d63-be35-fd8a0552eba9'
    Small_Pipe_Tee = 'e1273b8a-945b-4080-81eb-cbf79961cccb'
    Toilet_Paper = 'e2a0770b-9bb9-4b3b-b9f2-994b534b79f3'
    Tower_Pole_Top = 'e3e58881-69e6-4593-8211-017bcd72c907'
    Antenna = 'e585bcd6-5828-4a37-8ec7-dffb561f0956'
    Headlight = 'ed27f5e2-cac5-4a32-a5d9-49f116acc6af'
    Nut = 'edd445cc-c298-4ce3-9a58-745c1bee1bc7'
    Cucumber_Box = 'f0438bd7-6307-4991-943f-d78b04877d96'
    Wires_Convex_Bend = 'f0713386-8c95-493d-b013-e8e53e32d1ed'
    Small_Tank = 'f37b101c-508b-4630-9f9d-47ef1c834183'
    Staircase_Step = 'f5786e5d-8366-4ebf-be00-f3a4b036a77b'
    Carrot_Box = 'f6687d52-efc1-4f00-b573-bee4363ee14f'
    Tall_Shelf_Support = 'f80026c5-2019-4f87-8abd-345bd23aa156'
    Tower_Pole = 'f9e8707a-62f8-4051-84e9-c2e17b686d9e'
    Plant_Container = 'faae6e1a-f431-49fd-b8b8-16f12139ee88'
    Duct_End = 'fbc0fbfb-803c-42dd-aace-1ae10e55a785'
    Pillow = 'ff2207c1-e40b-416f-8bdd-66a9efd6d1a9'
    Off_Road_Suspension_2 = '00284190-1484-4286-a198-b2ddef768c2e'
    obj_survivalobject_elevatordoor_left = '004bb5ee-34ba-484a-924b-31412d898e7e'
    obj_spaceship_wall04 = '011c1ffd-7146-4e8d-8c18-17247d768ae2'
    Scrap_Stone = '02ee2a98-bd8d-4a09-bb69-38edaf66b8e1'
    Industrial_Beam_Four_Way = '04680945-5bb7-4a8a-9246-24c6c2b977d1'
    Small_Narrow_Warehouse_Ramp = '04733746-4090-4d63-aff1-47dafae506fd'
    obj_harvests_trees_pine03_p08 = '0539121b-9588-4c64-bdd0-25b0a29b081a'
    Gas_Container = '056e5ff1-f030-40df-946a-b830bf494c92'
    obj_harvests_trees_pine03_p09 = '05c81c17-3780-4edb-80a4-1648c25ca460'
    obj_harvests_trees_birch02_p04 = '06c564e2-ca8d-4843-94e9-322cb835f59e'
    Giant_Pipe_Glass_Straight = '06fd0e52-f791-43a6-9fbd-5a8a6260f3f2'
    obj_harvests_trees_birch03_p06 = '079b7a15-7718-444b-8560-7717109dabff'
    Berry_Billboard = '080ef1dd-07a7-4d31-86b8-ac907e1468bf'
    Scaffold_Frame = '094ceb5a-995b-431f-87f4-aac091494ae4'
    Potato_Ammo_Container = '096d4daf-639e-4947-a1a6-1890eaa94464'
    obj_harvests_trees_birch03_p01 = '0a2544c9-902d-42e2-91af-f35dad9c5d0e'
    obj_harvest_stonechunk01 = '0b114031-5065-4365-922d-3980d791e00d'
    obj_harvests_trees_birch03_p04 = '0b423e11-50dd-4272-92a2-506f42c992d4'
    Banana_Crate = '0bc74539-df8a-47c7-aad8-d55d809a01e4'
    Water_Dispenser = '0c077288-d15d-45d6-8439-3dabe7144034'
    Shack_Roof = '0c07dba0-be79-40fd-9ed8-5a1c34e2d196'
    Electric_Engine_2 = '0c9cc5bb-af2f-4023-b8d8-cd7d52a60efe'
    Mop_Set = '0dff60c2-f7ae-4c13-b9c4-962ec1039be8'
    Carpet_Roll = '0e695319-afd0-405b-85c8-289df8614c52'
    Warehouse_sink = '0ebf382a-e2e4-4c46-a48e-87808308c1e3'
    Encryptor_Holder = '0ee4fc0a-9f69-4d67-b5c2-09ea5a22712f'
    Broken_Concrete_Large = '0f638bd7-0c0d-4ba3-9ba2-af0b523ddff4'
    Ship_Compartment = '10079046-6400-42fd-bcd6-f66af6cfd8b8'
    obj_harvest_log_l02b = '10149368-0d49-44c1-9521-dbec436eb770'
    Water_Bucket = '798c2c81-1f8e-481b-8c32-b71b5dc5511a'
    Warehouse_Crate = '10590ecd-7d2f-4ff9-a6de-e749870ae8b8'
    obj_destructable_tape_acrosstheroom02 = '109d044d-6002-4779-be04-34501d78408f'
    Stand_Support_Corner = '109e1514-4f3b-4bd9-8d95-2d81fdb8fb25'
    Crude_Oil = '1147e59d-6940-42b4-840b-07f05054f5e0'
    obj_tool_handbook = '1226cfd3-4fc8-4f9e-b21a-0c9576e2ef2f'
    obj_harvests_stones_p04 = '126be16e-10c1-4ccd-82c5-368edc7f766a'
    obj_harvest_log_m01 = '135967d2-7faa-495f-98f4-5130350396a4'
    obj_harvests_trees_birch02_p01 = '13cf98bf-d033-4be5-a0a0-560cb946a4ba'
    obj_destructable_tape_taperoll04 = '1503a160-bf1f-4b86-8406-b11250c71a28'
    obj_harvests_trees_pine03_p10 = '15ee8b4c-d58b-462f-a0a0-5c9bcdff495f'
    Giant_Pipe_Glass_Corner = '16ed53cc-a45b-4f64-92d4-2db93bf33e1c'
    Frame_Beam_Corner = '176f4537-b245-4ba2-a318-da12e15bf789'
    Controller_2 = '1872d83a-d1a1-4cb7-ad46-9e4468d2548c'
    obj_destructable_tape_tape06 = '189aabd7-a3a4-4ba1-886e-e2e21dd1772b'
    Ship_Blinds = '196586b5-897f-40f3-926c-b5dfa4f772eb'
    obj_harvests_trees_pine02_p04 = '1986c34b-c318-4992-ab1d-34a1531a4095'
    Office_Table_A = '1991e0c6-4dd8-4e44-9da8-7fdf4d938fdc'
    Ship_Ventilation = '1aac8942-38ac-4a83-bc16-6d33436c0934'
    obj_harvests_trees_pine01_p07 = '1b24e0a4-3f04-4dfe-83ea-612da2eff922'
    Generator_Pipe_Tee = '1b47f36c-7c6e-451c-87b2-34fdf33d6989'
    Hollow_Concrete = '1b927252-ee6d-420e-8bb4-ae42fcb43ba8'
    obj_destructable_tape_rooftape04 = '1bace005-426c-4b44-8530-ef8698210a6f'
    obj_destructable_tape_tape02 = '1bdc2111-691c-465f-84d1-0e5faeca9897'
    Gas_Engine_1 = '1bfccc0a-828f-475c-882c-87d5a96054c9'
    Broccoli_Seed = '1c6756ca-3a60-4dcb-a5d1-353edf818308'
    Craftbot = 'c69a7855-d915-4784-af81-d0a8849e458f'
    Sensor_1 = '1d4793af-cb66-4628-804a-9d7404712643'
    obj_harvests_trees_birch01_p04 = '1d667253-849c-4f9f-9109-1a2d91795247'
    Stand_Support = '1dc643c9-6f8e-478a-8ebb-4adf3cb9960f'
    Tomato_Crate = '1dcd74ca-39ba-4b00-a36a-3381b25055f4'
    Ship_Floor_Tile = '1df6f1af-fd39-443a-9fd7-dd389e0ba5c8'
    Packing_Lamp = '1e2485d7-f600-406e-b348-9f0b7c1f5077'
    Office_Chair_Base = '1f343b76-3622-4e4b-9de4-238d43d60734'
    Master_Battery_Info_Board = '1f5d8b77-183c-4f8b-83d7-a3940d090926'
    Warehouse_Ventilation_Mount = '20821431-de44-4d54-8877-60833316104e'
    Large_Taperoll = '20b3577f-a2f1-44f3-a22c-83f792732771'
    Hard_Work_Sign = '20bd2885-d184-44ae-b72b-f90b786f8664'
    Sensor_5 = '20dcd41c-0a11-4668-9b00-97f278ce21af'
    obj_destructable_tape_corridor01 = '20e0b1f2-dd7b-4b69-9308-b6c26c0b0e6e'
    obj_harvests_trees_birch03_p03 = '2133fdb7-5e3c-4fb9-99ad-5b4f8bf5c6e5'
    Man_Sign = '221badef-0313-419c-9a7c-7469d26b0d5b'
    Sale_Sign = '2289e96f-f9c6-440c-b7c9-ce9474da8264'
    obj_harvests_trees_birch01_p01 = '22947bb1-7c64-477c-8656-d7857df39b78'
    Banana_Seed = '22beade5-38ca-47b4-a2ee-32403f58a862'
    Small_Ship_Corner_Floor_Mold = '22c526fc-b212-4e4e-af00-1cc69d9129e1'
    Electric_Engine_5 = '22f3e797-82f5-4819-a085-c3cc28ec9025'
    obj_harvests_trees_pine01_p10 = '2311afca-ca99-4b7b-a209-8382ed7ea356'
    Controller_4 = '2354cd24-3dd3-4db5-84ab-df64c32d2c72'
    Generator_Coil_Corner = '23572f75-03c0-4c33-b643-70250d0e4ae0'
    Cup_Holder = '239c9c71-e5c7-4ccb-ad40-7bdbb32f3cc9'
    Haystack = '23ac6823-51a4-4581-b8ca-061c76f093f6'
    obj_spaceship_wall06 = '2448a709-a8ec-4d69-a927-b9ab195cd83f'
    obj_survivalobject_elevatorfan = '256fde90-4225-4c22-b107-fcaabe2bec9c'
    Scaffold_Pallet_Ramp = '26119eb4-0e0e-4730-85ad-8a8c44f3d18c'
    obj_destructable_tape_big_walltape04 = '265bf568-a801-4ce6-8ac3-d20526443bc5'
    Ember = '267e0c93-62e3-45ad-9470-a14035cb9ca4'
    Ship_Ventilation_Panel = '275e4258-ff57-45ae-8e2f-b82204c56d16'
    Drill = '276fd55b-ae54-4a7a-ace6-fddd2d3370a5'
    Garment_Box_Rare = '27a221b1-9809-4df1-901a-caafe119c9b6'
    Fresh_Neon_Sign = '27c00cfb-4e7f-45fc-a037-f9a941464ce6'
    obj_destructable_tape_cocoon02 = '286faea5-83db-4f53-8813-1ce81309a059'
    Crane_Loading_Floor = '2893e707-36b3-4ff1-bb3c-ef1b5524ae13'
    Ship_Opening_Floor_Mold = '29c5c1eb-a3bd-45ae-b823-aeb28d70593a'
    Shack_Wall = '2aa8cb2c-2311-440c-8162-829ee394fbc2'
    Cookbot = '2af00456-b22e-4743-b338-a91934aba7c5'
    Seat_2 = '2b9c6e87-1b75-4a57-8979-74d9f95668ba'
    Elevator_Sign = '2bacc33e-60fb-40c3-b751-ef76f79392c7'
    Metal_Storage_Corner_C = '2bbaf389-4ef7-4dca-b7ee-397cc30f3862'
    obj_spaceship_wall12_damaged = '2bc619a3-c884-4e60-9e78-6c04487a48c5'
    Woc_Milk = '2c4a2633-153a-4800-ba3d-2ac0d993b9c8'
    Warehouse_Brick_Lamp = '2c90e412-9476-40d9-a440-228c888186bd'
    Saddle_1 = '2d3016f7-febe-416e-93bc-41d80ca3910d'
    obj_destructable_tape_rooftape03 = '2d503740-f2da-41a1-ae5c-3c49d44e3bb2'
    obj_tool_spudgun = '2d7f1278-ac93-4039-9eb2-d31715ea10ff'
    Chemical_Bucket = '2e792123-4a10-4cc6-b9ef-c5a518655cb4'
    Piston_5 = '2f004fdf-bfb0-46f3-a7ac-7711100bee0c'
    obj_harvests_trees_pine01_p08 = '2f955589-701b-4c47-9127-37feeb80d35a'
    Mini_Craftbot = '2ff2b13f-5a50-443c-bbda-1f40f6aa917f'
    Gas_Engine_5 = '3091926a-9340-46d9-83d6-4fd7c68ad950'
    obj_harvests_trees_spruce02_p02 = '3104311d-a1c6-4f26-8eb9-7eea54fe164f'
    Cash_Register = '31ada55e-7c79-4aee-86b6-809c0e5468df'
    Net_frame = '31c38d38-73f5-47ef-93c8-e10d4f579e1c'
    Piston_2 = '31f14f52-f4d8-4b9f-9d6e-7412497c9284'
    Large_Pipe_Extension = '3292878f-4d1e-49e3-a80f-16b710dad42e'
    Gas_Engine_2 = '33d01ddd-f32b-4a9a-87d6-efb6710b389c'
    Cotton = '3440440b-d362-4473-aa03-b7c41e1fe7ad'
    Trigger_Frame = '346a4ea9-d360-4133-b62f-4c188000c60b'
    Corner_Brace = '3526de39-dcf4-484b-84ec-3336538be192'
    Glue = '36335664-6e61-4d44-9876-54f9660a8565'
    Glow = '388adeab-67e5-4901-afe8-c56217754510'
    Power_Generator_Side = '38934d9d-69a8-4a1f-8137-892ede148cb4'
    Tomato_Seed = '38e41fb5-dd50-4294-829d-a517f0282fed'
    Seed_Container = '38ec258d-c644-4f08-8635-3f7434c884dd'
    obj_packingstation_crateload = '3a135dd2-510c-434b-b019-ce077042a5c8'
    Glowstick = '3a3280e4-03b6-4a4d-9e02-e348478213c9'
    Industrial_Beam_Corner = '3ac141b5-3fbe-4588-9679-c458ac07642a'
    obj_harvests_trees_spruce02_p05 = '3b0c9ff3-6c5a-404a-b830-4872471bf33f'
    obj_harvests_trees_leafy03_p01 = '3b30e244-edca-44c3-a2b8-08ae779c69e6'
    Encryptor_Frame_Beam = '3b47a99f-85c4-4490-8dc5-3560b7c4c863'
    Small_Warehouse_Ramp = '3b552b6f-2f32-4c1f-b9c4-ff9ff7dd0ac3'
    obj_harvests_trees_birch02_p06 = '3b683206-f4b6-4652-bb32-dd488e73f367'
    Seat_1 = '3b972f2f-30c7-4a5e-a100-5e257e62295d'
    Stone_Crate = '3bd4430f-75bc-452c-9e80-1bd639898689'
    Encryptor_Frame_Top = '3cbf5f08-14da-4db5-8360-de5078e7c4c1'
    obj_harvests_trees_leafy02_p04 = '3d9dd135-5e3d-412a-bb1b-2ad58f0ea8be'
    obj_destructable_tape_tape05 = '3db622ee-112b-4b72-97fc-5bf49c3edf15'
    Office_Table_Leg = '3de61f00-5782-40ca-923d-7efabe334572'
    obj_destructable_tape_cornertape01 = '3de7e8ca-f7f4-4faf-b348-4848741528c1'
    Saw_Blade = '3e10ef67-383a-4b60-aa5b-b1173134e437'
    obj_harvest_log_l02a = '3e6d2a8a-c836-4ae5-b6bf-9ec01c6393b0'
    obj_harvests_trees_pine03_p05 = '3f7c3f3c-9b28-4a26-abbd-8f2948e9b027'
    obj_tool_frier = '3faf624b-0a95-452f-b6cd-9930ad1731c5'
    obj_spaceship_wall02 = '4053c30c-6717-47c7-b0a9-177f7b8b30bc'
    Power_Station = '40c5b3fd-1ac4-47f4-ae61-503e14baf20f'
    Glue_Clam = '40e8bd0d-04a0-4e95-b593-4038b54b156f'
    obj_harvests_trees_leafy03_p02 = '40ff42d8-6e6f-4da4-a91c-8289e72b9ea1'
    obj_harvests_trees_leafy01_p00 = '4126d267-c8df-4c3c-98c7-9cb17f87f770'
    Large_Pipe_Compressor = '412dee88-996e-49c2-8b51-5644f659f9b2'
    Fan_Blade_Cap = '414854a9-77bc-48aa-a9d5-0c7cd213e4df'
    Giant_Pipe_Corner = '41784077-0636-470f-a6df-b868f152af29'
    Drivers_Saddle_4 = '41960868-6245-47b5-97c4-f446e199812f'
    Industrial_Beam_Corner_Bend = '419fb889-e440-420c-b553-4cdf95e71a61'
    obj_harvests_trees_leafy02_p03 = '42bac230-35c5-4d22-a141-1cf693137548'
    Saddle_5 = '42f70341-207d-4e9d-b8ed-37962603a926'
    Sound_Isolation_Large = '4369132a-40d8-47e7-ac45-e390c0ea6597'
    Metal_Storage_Support = '43c0ca80-0980-433a-88a3-929727a62a6d'
    Crane_Leg = '448d7d18-2a36-4749-8d73-3da913ae6aeb'
    obj_destructable_tape_doorwaytape01_destroyed = '45b6f45a-9b47-40af-88d1-f1ad0d98e565'
    obj_spaceship_corner01_damaged = '45ee9f5a-cfc0-4f3a-bbe8-09f2ce1dbc4c'
    Piston_3 = '46396518-8c29-4da9-81bb-a020f4baf5b2'
    Seat_4 = '46465697-ed36-4720-ba8a-08c568b4e36c'
    Warehouse_Ventilation_Long = '468650b4-5ff7-4be1-9e75-05ed86fd83e0'
    obj_harvests_trees_pine02_p00 = '46a78456-aa4f-409d-98d2-d1fdeac94e41'
    obj_spaceship_wall03 = '46ac20df-dfbc-434f-aaf3-f34ddc2afb42'
    obj_destructable_tape_cornertape02 = '46f4a939-b20c-4fae-bf37-8410796a05f2'
    Ship_Light = '47062936-5d28-43ec-81b5-8fdb619e97e4'
    Gas_Engine_3 = '470b9a92-ed94-4ef2-b1ea-b45f47ef0982'
    Warehouse_Sign = '4724913e-4f9b-4334-8408-4b0850a1c7de'
    obj_harvests_trees_birch02_p03 = '47b95667-6296-4bc4-a93e-8e2bf51c8b80'
    Office_Table_B = '47d33078-a9b0-4e30-9610-ad0556be5fa2'
    Carrot = '47ece75a-bfca-4e8a-b618-4f609fcea0da'
    obj_destructable_tape_rooftape01 = '48a0b91a-1edb-4695-ba61-c702570563ce'
    Large_Pipe_Cap = '49938942-fbb6-444d-bba6-1fb339ee5cf3'
    Blueberry_Seed = '4b6d2bee-d0f1-4e56-96f0-d2596388cad2'
    Bathroom_Stall_Door = '4c17571c-89b5-40f3-b13f-e9399591d0b4'
    Thruster_3 = '4c1cc8de-7af1-4f8e-a5c4-c583460af9e5'
    Off_Road_Suspension_4 = '4c3f6a7c-45c6-4ed8-bf13-c247c3db6b81'
    Office_Chair_Top = '4c93de5a-72ab-40d0-a081-c41e3aa87e86'
    obj_harvest_stonechunk03 = '4cd7a389-a1ac-47f4-8cc0-2776174985da'
    Redbeet = '4ce00048-f735-4fab-b978-5f405e60f48f'
    Sickle_Down_Billboard = '4d54298c-93a0-4b6d-8719-7380430a27bb'
    Packing_Table = '4db857f1-07dc-4ea2-9391-fd24903945d1'
    Ship_Floor_Mold = '4e084e1c-08e9-43de-bc6f-6fd73a9620aa'
    obj_harvest_stonechunk02 = '4e3f17bb-0169-4eb5-a4b4-84725a607b2c'
    Pineapple = '4ec64cda-1a5b-4465-88b4-5ea452c4a556'
    Net_frame_hatch = '4f5092dd-e2e5-4d42-8ec9-c0337cf23e21'
    obj_harvests_trees_pine03_p07 = '4f693e6e-7819-46ff-aef3-5cfd2fc5bbde'
    obj_packingstation_mid = '4fbf640a-200d-45c6-862a-cc2900f84f2c'
    obj_destructable_tape_cornertape03 = '50668b05-41de-4b48-abf2-6a576ab550fe'
    Metal_Storage_Floor = '513530b0-61bd-4b82-83e7-191d090d25d8'
    Sport_Suspension_5 = '52855106-a95c-4427-9970-3f227109b66d'
    Pizza_Burger = '54d84731-d9ec-435d-bc9d-d48e0763b1bf'
    Veggie_Burger = '54d8ef21-357d-48a3-a66d-40446f6bb686'
    Crane_Top = '54ea2236-001c-4560-8e6d-3942a885bb3b'
    Component_Kit = '5530e6a0-4748-4926-b134-50ca9ecb9dcf'
    obj_destructable_tape_tape04 = '55597dd3-44b6-4fd5-81da-bb56d2ec59d9'
    obj_harvests_trees_birch01_p00 = '55b19e7f-e45b-48b2-8f7c-d9e84fed0736'
    Electric_Engine_3 = '56cea967-a685-494d-85ef-3aa121a0c193'
    obj_harvests_trees_leafy03_p06 = '57d39e43-5c0b-476c-b8a2-474c77c22607'
    Holder_Support_Leg_Base = '5888a6dd-59ab-4cd6-86b2-6e68f64674b5'
    Vacuum_Pipe_Corner = '5939f460-ab6c-48f2-9d07-a66845ce8cf2'
    Controller_1 = '598d865c-324c-4129-9c57-21a6abd2cb2e'
    Vacuum_Pipe_1 = '59ea6ce8-239b-4eed-8847-a51b907d9b42'
    Scrap_Wheel = '59f6951a-a450-42bf-ad03-54567cb70245'
    obj_harvests_trees_leafy02_p06 = '5a0ffe5b-f7cf-482b-915f-1d6b0876c26c'
    obj_harvests_trees_spruce02_p00 = '5a508601-485f-4db6-8134-69a4d3d02bc1'
    Sunshake_Vending_Machine = '5ad298e4-f5ad-479c-9ec6-6c4f9d3fb8ae'
    Calendar = '5b628f22-ec0d-448f-a6be-3453950120a4'
    Ship_Wall_Panel_Small = '5ba206c2-d10b-4815-b95b-04be4959ec31'
    obj_harvests_trees_pine01_p06 = '5ca61a85-7040-47bc-8f87-5d2ce295cb6e'
    Refinebot = '5cb15c93-4fa9-48da-9974-2e95ca6c9e1c'
    Scrap_Metal = '5cb39ea5-554d-4c40-9d9a-6b2dd59de953'
    Generator_A = '5cd67a6e-52cc-4eb0-9f44-275d366516c5'
    obj_harvests_trees_leafy02_p02 = '5cf2c67c-62f6-4219-a857-943901611c6f'
    obj_spaceship_wall08_damaged = '5d2cdb56-2be8-4a62-8f05-ce5c9c1510ac'
    Warehouse_Square_Light = '5e3dff9b-2450-44ae-ad46-d2f6b5148cbf'
    Electric_Engine_4 = '5e57e0f7-e87c-4269-b274-146fe40e1b44'
    Electric_Engine_1 = '5e5d231e-405e-4f45-9bd0-b3557dbb42eb'
    Respawn_Bed = '5eb8975b-0acf-43a7-ab4e-62ce661c0df7'
    obj_harvests_trees_birch01_p02 = '5ee9b950-839f-479a-bc06-902b830504cf'
    Ship_Shelf = '5f5926f5-1449-49b0-8997-2d5a0df37b21'
    obj_survivalobject_elevatorceiling = '5ff56026-7af2-4644-b30c-f0b43230093f'
    Large_Narrow_Warehouse_Ramp = '60075229-2e4e-4aeb-9e64-da41b6ac9611'
    obj_harvests_trees_pine01_p01 = '608d6e20-bc3e-4440-907f-f0bd5fb45eac'
    Industrial_Beam_Short = '6130d484-775e-481a-889a-43d2e8d29058'
    obj_hideout_questgiver = '614c3193-13da-40f4-9b03-37f26e760fd6'
    obj_spaceship_wall12 = '6159898f-beb8-4f49-825b-92b0774daa61'
    Call_Button = '61bdf048-c09f-4cf5-8b47-35ba28c0580c'
    obj_harvests_trees_pine02_p03 = '61f24d00-3d2d-44bf-818e-50a11c920aca'
    Cement_Mix = '6232b62a-f3e0-4609-a159-ab08abf8125f'
    Redbeet_Crate = '628fd350-577d-413f-82a8-7f08a83de3d8'
    Garment_Box_Common = '63695efd-0862-49f2-ace6-4d1758147fae'
    Giant_Pipe = '63cf0973-b81e-4fe1-ae44-654937e1b0e4'
    Redbeet_Seed = '64051718-a3f1-422b-bda3-277efa0c4545'
    obj_harvests_trees_birch01_p05 = '64555383-f1c9-4027-a1c4-02951d085b76'
    Rounded_Frame_Corner = '64fdc73f-259a-49df-94ac-24db25a4dc42'
    Old_Restroom_Mirror = '659488be-3d33-4244-b762-e7d77dcdcbbe'
    Large_Pipe_Mount = '6661da68-74af-4425-ad63-d5b4631ee266'
    Metal_Storage_Ramp = '66affe90-4552-455e-a0b0-b203f9988790'
    Ship_Ceiling_Ventilation = '66c1ccc6-1a68-40f3-9e10-ee362c3c13bc'
    Giant_Pipe_Holder = '66c3a5cd-ce37-4b37-916d-ac39a67ad2f5'
    Sport_Suspension_1 = '67da25c9-3825-41f6-9724-4546a11cb2a5'
    Generator_Tank = '684002ad-3218-4dd0-a6dd-53e6dfdec562'
    Ship_Wiring_Short = '68d8eeb6-14e4-469b-9ee6-f80ebe1c4be6'
    Sound_Isolation_Small_ = '68db6d52-00fb-441a-ab34-a79341acde32'
    Drivers_Saddle_3 = '6953b17e-0a38-4107-8c56-5ee97e68bee3'
    Water_Cannon = '69559e81-50fa-40ae-afa2-a22c1a49eb54'
    Blueberry = '6a43fff2-8c6d-4460-9f44-e5483b5267dd'
    obj_packingstation_screen_veggie = '6a620faa-ca0d-4e39-bc67-97fb93d808c2'
    Fan_Base = '6ad9b8c7-4006-43cd-aa95-3d63c0e5c9fb'
    Controller_3 = '6bb84152-c4d7-4644-bc37-a3becd79298d'
    Banner_Holder = '6cb18801-8284-4f27-9f2e-b9955861b605'
    Tomato = '6d92d8e7-25e9-4698-b83d-a64dc97978c8'
    obj_harvests_trees_leafy03_p04 = '6e7eb9bb-4b8e-400a-b9c4-2e9320e03ead'
    Concave_Wedge = '6f38a734-571f-4c3d-97b9-c0aa480973af'
    Steel_Support_Bracket = '6f699ce5-4955-4725-9829-2b6e1dd6eee9'
    obj_harvests_trees_pine02_p06 = '6f89ff7b-f49d-4f6e-904a-5758c29b0d8e'
    Seat_5 = '703ca746-d802-4e76-b443-4881e83afb73'
    Holder_Support_Leg = '70a497d6-6bc2-4ee6-a381-0976d68ac980'
    Hideout_Button = '712a5ebd-0793-49ba-b1ef-681a8fdceba6'
    Unfolded_Grow_Box = '71665314-db59-4c43-bfe2-2746baa8ffe9'
    Wrapping_Roll = '72074131-529b-49c1-9ff3-73706f61eb06'
    Ventilation_Frame = '7237080a-676b-4be1-bb7f-2fb1a9f6f274'
    obj_tool_paint = '731c6a84-7ae7-439d-a620-128076f9985c'
    Piston_4 = '7324219e-2b19-4098-baa3-9876984ead08'
    obj_harvests_trees_pine03_p00 = '737a5987-a586-4a06-9e9d-3661ab8d69d2'
    Off_Road_Suspension_5 = '73f838db-783e-4a41-bc0f-9008967780f3'
    Metal = '7468db55-b29d-4ce0-82b9-2414f493a376'
    Vacuum_Pipe_5 = '7479ff7f-37fc-4304-93e9-aad7891c29f2'
    Hay_Bale = '74a3f240-65b2-4f52-9555-9b52173fca0a'
    Saddle_4 = '7516f5b8-9a15-4606-92bb-ea9a96a16594'
    Old_Fruit_Stand = '7540ef9a-5c84-4dd2-b111-176d8de66e47'
    obj_packingstation_front = '75c11f33-7592-427f-96ac-d89994438042'
    Fertilizer_Container = '76331bbf-abbd-4b8d-bb54-f721a5b6193b'
    Warehouse_Ventilation_Short = '764e94d1-61c0-4fef-9719-5548889e4817'
    Dressbot = '767a3121-2c31-473c-a5ab-27e188fdd55a'
    Office_Sign = '7728c105-1fd9-4aaa-95ec-1da45b425d89'
    Drivers_Seat_1 = '77c2687c-2e13-4df8-996a-96fb26d75ee0'
    Saddle_3 = '797e07a3-6d56-4b74-949b-9492c7946e0d'
    Generator_C = '7997f4a5-6f5f-492e-95cb-65a5e2a0f2f2'
    Ruin_Chest = '79cc711e-7094-4029-8419-bbbf8f08c6f2'
    obj_harvests_trees_pine01_p05 = '79e41f5c-7b69-42ba-9172-7e3df49231bd'
    obj_harvests_trees_pine02_p08 = '7a31b721-c944-4b40-ba71-c1b2e3f00b9c'
    Garment_Box_Epic = '7ab0cac7-b055-4283-b0bc-f85dd4d0416b'
    Warehouse_Fluorescent_Light = '7b2c96af-a4a1-420e-9370-ea5b58f23a7e'
    obj_harvests_trees_birch01_p03 = '7b78d74f-c4c7-4c48-80f5-8f7f4bbd5de9'
    obj_destructable_tape_tape03 = '7ba75948-640c-4563-9501-800cbddbeb6d'
    Road_Sign_Base = '7bc20d55-6b49-450c-830c-16282ce7fb2d'
    Drivers_Saddle_1 = '7d601a5a-796d-4cae-be88-b47479d38d11'
    Blueberry_Juice_Cylinder = '7e2b1dcb-4853-43ed-a7c5-0eb1a24b49d0'
    Large_Warehouse_Ramp = '7f0d8b7c-861f-4597-94b4-a87978b3f750'
    Ship_Wall_Panel_Medium = '7fa4ecf6-d8fe-49eb-a950-db1fb4590c4d'
    Generator_Coil_Segment = '7feba511-4910-429d-a0e3-f1727259ae5c'
    obj_harvests_trees_pine02_p10 = '8089b86c-7390-4cb6-b30e-7b281e8c329e'
    Scaffold_Plastic_Wall = '82625879-3a0a-4ab8-9895-575d38ec4420'
    Frame_Beam_Short = '82694546-92b2-47c3-894d-7fc215e2de4a'
    Giant_Pipe_Tee = '8310f5b9-3394-4723-ac23-f59a21d6e3f3'
    Small_Taperolls = '8365cf6a-af1a-41aa-a8c9-34313dce1f55'
    obj_tool_weld = '836e98a2-8c8c-4a6b-9239-54acdd4f4736'
    Generator_Pipe_Long = '838c8d9a-8fc0-4b15-898b-b82bbf8bf2e0'
    Scrap_Seat = '847daf20-02bf-4170-8699-9ab106acd29a'
    obj_spaceship_wall05 = '84d8e6eb-948b-4dd4-ab23-55a64d33eff1'
    Warehouse_Spot_Small = '85339a1d-e67f-4c63-94fd-4a1cf8c25810'
    Generator_Pipe_Corner = '85623170-074a-4663-8944-97d131aff495'
    obj_harvests_trees_pine03_p04 = '85a54457-4172-4be5-a750-96df4d40286c'
    obj_tool_connect = '85fc5f11-722b-4723-91f2-293a81ad0800'
    Oily_Toilet_Seat = '8694192c-d91b-444c-a184-910911bbb354'
    Water = '869d4736-289a-4952-96cd-8a40117a2d28'
    Generator_Pipe_Short = '872ae33f-cf02-4959-91d0-ead1dacfd34b'
    Scaffold_Plank = '87a3bc6b-5eb3-43a3-871a-0cb42a415d64'
    obj_harvests_trees_leafy03_p03 = '8821ec7c-477d-4d3b-9b0c-aee479d3e6c3'
    Utility_Sign = '884080be-c723-4e6e-828b-6019af8beed6'
    obj_harvest_log_s01 = '88dc2a60-7e1a-4c24-8584-2491acd79753'
    obj_harvests_trees_leafy01_p04 = '88dc4f4a-18c2-4d79-8dee-f0e7ac9d5845'
    obj_harvests_trees_birch02_p00 = '89ca09da-4e7c-404f-99eb-beb275cfc217'
    obj_destructable_tape_doorwaytape01 = '89f446fa-ba6a-4728-93b5-6a1abda114fc'
    Unfolded_Banana_Box = '8a4a55b0-0228-4839-933b-0716cedb3f96'
    obj_harvests_trees_pine03_p01 = '8c0a32e1-50a4-4e23-be1d-a09d12fc65c1'
    obj_harvests_stones_p05 = '8c0ad43a-4bc8-41ef-ab3a-de70eb9ef510'
    Piston_1 = '8c741785-5eae-4c48-9f99-d62bf522a83f'
    Generator_B = '8ca9a4f2-c8c8-439d-9945-e2e95dafbc21'
    Caged_Farmer = '8d601982-4608-4d5e-bb9e-e4041486f7c7'
    obj_harvests_trees_pine03_p06 = '8e2dfa65-c08e-4f51-a007-5fed80d846a3'
    Crane_Panel = '8f5f8a39-734d-4bc3-8a9e-74026bcb3704'
    obj_harvests_trees_spruce03_p05 = '8f9e059a-4c3a-4664-967a-28f127529aaf'
    Encryptor_Anti_Connection = '8fd2cf31-70b3-499a-bfb0-7e3d2c580258'
    obj_spaceship_corner03 = '90686663-1a3e-479a-b1c4-f81699274f50'
    File_Cabinet = '90dbaebf-8ea1-4a5a-8f6f-86ddde77c6c8'
    obj_harvests_trees_leafy01_p03 = '90f31b94-a831-4786-a5e7-6d423c224718'
    Sensor_3 = '90fc3603-3544-4254-97ef-ea6723510961'
    Battery = '910a7f2c-52b0-46eb-8873-ad13255539af'
    Encryptor_Base = '916cbfc2-776f-49d4-838a-eb946136be3e'
    obj_harvests_trees_leafy03_p05 = '92a6186b-9c42-48d0-9ebc-a978044e6a22'
    obj_harvests_stones_p06 = '92bae57d-ae30-4a75-a7ad-8bf91f20d660'
    obj_harvests_trees_pine01_p02 = '93ace99a-f58c-4dd3-8334-0ee890e42feb'
    Cotton_Seed = '93c27ab2-4930-4654-ba1c-bcfe35e966f6'
    Scaffold_Ledger = '93e32c6b-b9de-4fed-ad9d-49f0850ee634'
    Metal_Storage_Corner_A = '94acfb72-c650-4cb5-a8aa-08af3e691d2e'
    obj_destructable_tape_corridor02 = '94cf22f0-f0fb-4d1b-b5ce-f4b54e8e84d1'
    obj_harvests_trees_pine02_p02 = '9518dd16-f207-4dd5-9c52-91a655446a80'
    obj_destructable_tape_acrosstheroom03 = '960c9498-f76a-4ffc-a608-218dc6909de8'
    Crane_Hook = '96392e20-12e9-4a19-8dc5-7a8e33238ae2'
    Scrap_Wood = '968de65c-75f3-471b-954e-6165a4b6d3d6'
    obj_construction_signcone_taped = '9769c4b2-67f0-446b-a00d-ee432218b038'
    Giant_Pipe_Bracer = '9777f897-4cce-4c22-99ce-793aaca9f7c0'
    Vacuum_Pump = '97f449b6-c948-448b-b8b3-4448e3f6b956'
    obj_spaceship_corner02 = '988b5592-9e53-4782-a058-d26be442bd49'
    Ship_Dual_fan = '98ef8fca-d4a3-4b9a-8699-0630b003b9fa'
    Broccoli_Crate = '99477093-e819-4199-b62a-fda6143aae89'
    obj_survivalobject_cardreader_arm = '9a3058f3-6771-464f-a3e0-25d247f1422f'
    Soil_Bag = '9a3e478c-2224-44fa-887c-239965bd05ad'
    obj_destructable_tape_rooftape02 = '9b4a43c3-4950-49e2-858e-34768550a227'
    Stand_Support_A = '9b4ea447-9cd9-4cd1-84d5-8c414890e523'
    Vacuum_Pipe = '9b8f2abd-265c-4750-b8b9-fe6cb564633c'
    Ship_Wall_Panel_Large = 'a7d719f5-e839-4a95-923c-981b4dc21125'
    Carrot_Seed = '9c82a525-8a8b-4483-9595-505aaa042486'
    obj_harvests_trees_leafy02_p05 = '9ca81758-7c90-4368-ab57-1d9d62b32a37'
    Carrot_Crate = '9cd8288c-5a19-479f-af47-9eb55230ade2'
    Drivers_Saddle_5 = '9dd1ccea-1e44-430d-b706-3ff45416583e'
    Warehouse_Ventilation_Corner = '9e9280f7-c9bc-4b86-b788-43f9b48903dd'
    Pineapple_Seed = '9edb6f7c-fb44-4348-a1c4-8afb41b92d8a'
    Carpet_Spool_Holder = '9f909330-869e-468b-822a-204876118c0a'
    Thruster_2 = '9fc793b2-250b-40ab-bcb3-97cf97c7b481'
    Tomato_Juice_Cylinder = 'a0654dd8-f36a-4c41-bafd-18d9e5f0df2e'
    Controller_5 = 'a092359d-5cea-484d-a274-470d9a567632'
    obj_harvests_trees_pine03_p02 = 'a20e79dd-d74e-4e10-845a-b101b3a95ab2'
    Packing_Table_Holder = 'a2cf56fe-9961-481b-9a12-093f64867d9c'
    obj_harvest_log_l01 = 'a4ab4df5-403d-4baa-a3c3-ecc19dd87340'
    Elevator_Button = 'a553bf2f-3a66-404a-b4c6-ce9e7b73f9d4'
    Beacon = 'a5985971-1f95-4373-a5d9-4ce0a3e74851'
    obj_harvests_trees_leafy03_p08 = 'a6523fd2-869c-4d11-ba42-dc967a8aad25'
    obj_destructable_tape_corridor03 = 'a6524403-668d-4e41-93a7-6326e9205560'
    obj_harvests_trees_spruce02_p04 = 'a68470c8-67f4-4248-8c76-15fa7fb09ec6'
    Thruster_5 = 'a736ffdf-22c1-40f2-8e40-988cab7c0559'
    obj_harvests_trees_birch03_p02 = 'a73f7005-b89a-427d-8e94-c3d6f729be52'
    Vacuum_Pipe_2 = 'a77a3c86-ba12-4f1f-986c-4bb532c5105d'
    Large_Ship_Corner_Floor_Mold = 'a79a2bc9-1015-4c25-ab4b-0d4cb715db47'
    License_Plate = 'a7fb4293-f623-4a0f-9465-8bc640f0038b'
    Industrial_Beam_Long = 'a914fcb5-2509-428e-b8ad-80bf28af9f65'
    Resource_Collector = 'a930a42f-63ed-4fb0-933e-56ce8a889cc5'
    Off_Road_Suspension_3 = 'a9658eaf-0dd8-46a6-8cac-be6978f19b79'
    Large_Ship_Floor_Mold = 'aa3e38ef-21aa-4430-ab56-93c367f4f458'
    Banana = 'aa4c9c5e-7fc6-4c27-967f-c550e551c872'
    Sport_Suspension_2 = 'aae686a2-0eb3-43b3-b998-def282de79e9'
    Frame_Beam_Light = 'abaef792-741e-4c6b-8e79-02461a37b035'
    Fertilizer = 'ac0b5b0a-14e1-4b31-8944-0a351fbfcc67'
    Broken_Concrete_Medium = 'ac59ef69-95a7-4907-a8ba-e5c83ef83112'
    Packing_Sign = 'acc00050-d40e-42e9-9c2e-22ec2109dc3e'
    Large_Chest = 'ad35f7e6-af8f-40fa-aef4-77d827ac8a8a'
    Generator_Pipe_Holder = 'ad9f6357-b0b4-4dab-b84e-fb20df54d1ac'
    Generator_D = 'af389b10-a31b-46f7-bbe9-0bfad8181e97'
    obj_harvests_trees_pine02_p05 = 'aff3fcf0-9b67-42b5-bced-5acdf223c9aa'
    obj_harvests_trees_leafy02_p07 = 'b1647259-50bd-4838-814a-bfddd770ba70'
    Stand_Support_Base = 'b1c6bac0-4055-4193-8490-7704d0ea7113'
    obj_harvests_trees_pine02_p07 = 'b2c6c47e-7443-4566-a194-d3f24435733d'
    Holder_Support_Bend = 'b2c933a8-2dfb-479f-a3d9-b87797d5e0c6'
    obj_harvests_stones_p02 = 'b2d9e40b-e8e8-4d1e-86f9-86d0bdc5ddc4'
    Large_Metal_Storage_Lamp = 'b3425d6d-ea3d-45de-9078-10af2e178389'
    Handle = 'b3761216-dfc4-4679-960b-00f5ae5f8258'
    obj_spaceship_wall01 = 'b3bb8083-d9b5-408d-b45c-49a444efba57'
    obj_office_waterdispensertank_taped = 'b4831236-a9b3-4422-92da-803f9252a279'
    Broccoli = 'b5cdd503-fe1c-482b-86ab-6a5d2cc4fc8f'
    Cubicle_Wall = 'b627c533-f0e7-4fa7-83e6-5c3d517568e0'
    obj_tool_spudling = 'b633c3ee-2cda-4096-989a-60e90cd220aa'
    obj_harvests_trees_birch03_p00 = 'b7756219-75f2-4eb8-93d1-262e8ddded27'
    Metal_Storage_Corner_B = 'b7e60b8e-2075-4ae4-b906-53af3845e198'
    Shack_Half_Wall = 'b94a113d-ddd4-45db-844c-1d97ca0e1d61'
    obj_harvests_trees_spruce02_p01 = 'b95bcc20-9581-4228-b444-b1c7ebc73507'
    Metal_Storage_Beam = 'ba7775ef-d03b-46bd-aa09-09015297a415'
    Encryptor_Sign = 'ba79e3c0-914f-46ff-874b-243df5589e3c'
    obj_harvests_trees_spruce01_p05 = 'bb14330f-4698-4c2b-a5ba-732443a67d72'
    Drivers_Saddle_2 = 'bb2ed406-f0d3-4fd6-b3f9-7caadfa8e4e4'
    Pineapple_Crate = 'bc69cb3b-7e0c-4c36-805d-f8d89fcfced3'
    obj_harvests_trees_leafy02_p01 = 'bd2af8d6-ecc4-4071-82cb-56620345c06e'
    Scrap_Drivers_Seat = 'bd597ac9-6640-43ba-9bd8-ed584a794f13'
    Frame_Beam_Long = 'bdb55551-39a4-437c-aeff-f54368b19b5e'
    Chemical_Container = 'be29592a-ef58-4b1d-b18c-895023abd27f'
    Master_Switch = 'be744e84-f67e-4c06-a809-c247adc1babb'
    Orange_Seed = 'bee966b0-b5e5-41da-b992-5d363ab85ae4'
    Vacuum_Pipe_4 = 'bf7b6484-8b8b-4846-8110-c5d9f0b9ada7'
    Gas_Engine_4 = 'bfcaac1a-5a7f-4fba-9980-1159617a7212'
    Potato = 'bfcfac34-db0f-42d6-bd0c-74a7a5c95e82'
    Master_Battery_Socket = 'c0159b96-edf3-46cd-9fbe-96ee1126304b'
    Orange_Crate = 'c10a77d5-3357-4cb4-8113-a2cbe69c7ff2'
    obj_harvests_trees_pine01_p09 = 'c1593ec8-ed29-4f95-8bce-507f028810d2'
    obj_harvests_trees_leafy03_p07 = 'c1e99269-4090-489f-bcaf-f7cb04b03a73'
    Barrier_Stand = 'c2078bfe-fa3d-4c2b-8d97-6b5308ff624b'
    Fan_Blade = 'c2ce40b1-fc95-48bd-bd05-9c3e394a157a'
    Generator_E = 'c349afdf-aded-47bc-9a5c-606372bc535b'
    Saddle_2 = 'c39b3537-d9b2-45f8-b2ea-0e9002c896d9'
    Broken_Concrete_Small = 'c3a520b3-8d0e-435c-8070-e0ef58d028be'
    obj_destructable_tape_cocoon01 = 'c3b7163e-02d4-4b00-96ad-c15860be9419'
    Drivers_Seat_3 = 'c3ef3008-9367-4ab7-813a-24195d63e5a3'
    Elevator_Lamp = 'c4a0a65b-3b24-4beb-bd7a-d687f4210169'
    Crane_Wheel = 'c4aa3807-0806-4202-a36d-b5fa254d3046'
    Shack_Awning = 'c4ec4d33-83f7-4e7e-bb0a-8df52f96aef5'
    obj_harvests_trees_leafy01_p02 = 'c52c6da1-dad9-4649-b02f-34dec0bbd411'
    Bed = 'c563df47-9a8a-4338-9fec-06da1218c573'
    Diagonal_Ship_Floor_Mold = 'c5bdb30e-9675-4f8a-8fb9-07e5b98039d4'
    obj_destructable_tape_taperoll03 = 'c5d4f725-0a67-4902-b6da-82a16aafd36a'
    Master_Battery = 'c654a023-ca53-4109-9f18-d297c18e9a02'
    obj_harvests_trees_pine01_p03 = 'c713ed53-14fc-4a0d-93cf-9c2c865a2086'
    Paint_Ammo = 'c7322cd1-3158-41d9-b15a-eff2f2f8d9f7'
    Hay_Crate = 'c76b89a3-7731-4ae1-99d4-788a29319360'
    Traffic_Sign = 'c7772f74-f120-4008-8121-977e52a1d7c0'
    obj_spaceship_wall02_damaged = 'c807b38c-52b6-45cf-8cd3-1a46e6a9627f'
    Generator_Pipe_Four_Way = 'c85957a1-c393-4352-ba79-5004bb4f07a2'
    obj_survivalobject_elevatorwallleft = 'c8650c34-30ec-42c5-8dc3-7652ba4034ff'
    Protector_Anti_Destruction = 'c8b1bc7b-304e-44ce-9ca1-937b8e69d70c'
    Shack_Shade_Sails = 'c8ca8731-3af2-4554-9019-6b941affcb16'
    obj_destructable_tape_taperoll01 = 'c8d3b9ba-5bb1-49c5-aeb0-6c32f9b1e5c8'
    Pigment_Flower = 'c9396a42-67c3-4fa3-b682-31428ff9eced'
    Scrap_Gas_Engine = 'c96ab903-f238-4bae-a614-28a758716d00'
    obj_harvests_stones_p03 = 'c9d61f53-ebd3-4bb5-8789-43b00edbcc8b'
    obj_harvests_trees_pine02_p09 = 'ca208216-99f0-43d1-900d-cb0924223b65'
    Sunshake = 'cb7305b2-d8b5-4302-aff3-6cdd9212ca64'
    Crane_Cable_Roll = 'cbc6fc23-dcc9-4d6f-a7aa-9a3ae37ca41f'
    Protector_Sign = 'cc454365-7262-4953-a190-4bead4f4a260'
    obj_packingstation_screen_fruit = 'cc7fdd4a-ae17-44c8-9f91-089ea00f4891'
    obj_harvests_stones_p01 = 'cd18840d-d4ee-4f36-8ab1-843c823b0dcf'
    obj_destructable_tape_taperoll02 = 'ce1117c1-35d4-4c77-9a31-740078c6b1d8'
    obj_harvests_trees_birch02_p02 = 'ce37c509-2be6-4368-8ac7-a34a75fab248'
    Slippery_Surface_Sign = 'ce66734b-2122-460e-94dc-ccc73d799e32'
    Sensor_2 = 'cf46678b-c947-4267-ba85-f66930f5faa4'
    Pack_Instruction_Sign = 'cf4daf85-36a2-479f-96dc-b6201bc12d36'
    obj_harvests_trees_birch03_p05 = 'd00f05c6-f704-49a0-acdc-b4391086d254'
    Recycling_Bin = 'd053adac-e217-49de-b184-ad4bfbe1e52d'
    Sport_Suspension_3 = 'd0aa2676-5266-432a-bf7e-3887e6ddedd5'
    Locker = 'd0afb527-e786-4a22-a907-6da7e7cba8cb'
    obj_hideout_dropoff = 'd1840356-ad77-4505-a9a0-10d11a77986f'
    obj_survivalobject_elevatorwallright = 'd2093f3c-178c-4220-bfe0-e8a3d87f96c0'
    Main_Humidifier = 'd296c1ad-e893-4866-ba73-1cbbb38ebd37'
    obj_survivalobject_elevatorfloor = 'd2e0d468-858b-4a8b-98b4-8c5900309aef'
    Drivers_Seat_4 = 'd30dcd12-ec39-43b9-a115-44c08e1b9091'
    Stacked_Crates = 'd361b477-69b2-4a3a-b119-ec99a3938f5b'
    Frame_Beam_End = 'd42cae51-343e-4847-83a4-e55c1b04aa80'
    Open_Sign = 'd4ae8963-40e9-4680-934d-5626a3bfc363'
    Gasoline = 'd4d68946-aa03-4b8f-b1af-96b81ad4e305'
    Broken_Microwave = 'd4e6c84c-a493-44b1-81aa-4f4741ea3ed8'
    Sport_Suspension_4 = 'd9adddcc-972d-4726-a376-67f950b99a44'
    obj_office_officechair_taped = 'da2efa37-370d-4848-bc2e-2bae01173ce1'
    Battery_Container = 'da4833fd-f981-4e08-a9f7-48e630a7c146'
    Work_Light = 'da6e54df-a223-4a0e-b42f-ddeddd33f5b3'
    Paper_Stack = 'da86d1c6-e29b-4741-8b65-eed067222dc7'
    Paint_Bucket = 'dac97219-d076-41db-8bbb-2509facf0eb4'
    Udder_Decoration = 'db2ce519-490e-4432-b329-c973ecc8f5d9'
    Encryptor_Base_Plate = 'ddaa82ea-22c5-4a2c-8367-c2ee12d5ea5b'
    Sensor_4 = 'de018bc6-1db5-492c-bfec-045e63f9d64b'
    obj_harvests_trees_birch02_p05 = 'de556b89-a4be-4d7e-ab49-e6485af16836'
    obj_harvests_trees_spruce02_p03 = 'de637191-d84d-4c1e-8a55-7bb86e54ce70'
    Scaffolding_Step = 'de7a75db-207d-48fe-a385-fc4c61b40cf6'
    K_O__Bag = 'de7eea5b-9262-476b-a5bb-238d0e91f81f'
    Woc_Crate = 'deabb19a-1acd-4bbf-8bd2-f8f17410170b'
    Ship_Wiring_End = 'def1fe25-a33d-405b-ac04-2c1707c2101b'
    obj_destructable_tape_tape01 = 'df4724fa-b3ea-438d-b07f-75af46af4bfd'
    Thruster_1 = 'df8528ed-15ad-4a39-a33a-698880684001'
    obj_destructable_tape_cornertape04 = 'dfcff000-e027-4f43-9bfb-f9a84b3b50c4'
    obj_destructable_tape_big_walltape03 = 'e086d2de-6224-4ebc-8152-add18793ee58'
    Woman_Sign = 'e08d860d-650e-4b81-8cfa-411ea8e6e9c0'
    Warehouse_Ventilation_Drum = 'e0f8dc49-c418-403b-a7a1-44bea7ecd3d0'
    Stand_Support_Long = 'e22c8acb-151f-4837-ba32-7c61896b4eec'
    Revival_Baguette = 'e243f642-6934-42bb-8cdd-f8ff1704d411'
    Industrial_Beam_Crossing = 'e2844132-31b4-4a2c-af5f-0abd173af1ef'
    obj_harvests_trees_pine03_p03 = 'e3bc44d7-2173-47c0-86c3-0a9348812692'
    Warehouse_Key = 'e49b210a-0d46-4f06-bcd8-08862379d156'
    obj_harvests_trees_pine01_p04 = 'e4df268d-5845-4532-ba75-75bb7b71fcdf'
    Capsule_Door = 'e59afe5b-2c5f-4934-95d7-8c187b22fd6d'
    Thruster_4 = 'e6db321c-6f98-47f6-9f7f-4e6794a62cb8'
    Storage_Sign = 'e71b55c7-8547-4bef-bb77-e976c8abde0b'
    Blueberry_Crate = 'e77d9577-589a-446b-96c1-f6d0d7495489'
    Water_Tank = 'e7eae129-9e3f-45d2-997c-637865c60a5e'
    Warehouse_Ventilation_Tee = 'e846e3e7-b608-49c9-bbfd-e0bb859e6d3c'
    obj_destructable_tape_acrosstheroom01 = 'e8beb527-e470-4934-bc06-0d7f6312e49c'
    Ship_Wiring_Long = 'e8cadcb0-9cdf-49d8-bac2-00193e8ac3cc'
    Warehouse_Wall_Light = 'e91b0bf2-dafa-439e-a503-286e91461bb0'
    obj_destructable_tape_big_walltape02 = 'e9a7a26a-6e72-4bd4-8a44-7d5ab8b83f4b'
    Water_Container = 'ea10d1af-b97a-46fb-8895-dfd1becb53bb'
    obj_destructable_tape_big_walltape05 = 'ea16ec2e-5135-49e9-9543-9bdcd818d90a'
    Metallic_Tube = 'ea64acf0-c0a8-44c4-a946-f358d232e965'
    Metallic_Tube_Straight = 'eabc9e68-6172-4719-ace5-5d64333233c0'
    Potato_Seed = 'eb1ef696-5c05-4662-9e47-fe1e0875ff84'
    Metallic_Tube_Bend = 'eb608c5d-c418-49db-a2c5-1c8186b3d314'
    obj_survivalobject_dispenserbot = 'ebd73cee-988f-4ffb-95d1-d3c3c81fd506'
    Seat_3 = 'ebe2782e-a4f5-4d91-83cc-db110179393b'
    Shack_Light = 'ebefa387-fe4a-4839-bdd9-b6b4da39368f'
    Ship_Terminal = 'ec0bb005-f3c1-425a-94c4-6feca8567068'
    Crane_Body = 'ec334737-1467-4a29-a3b7-e04f662bca1b'
    Construction_Pallet = 'ec757a7d-a27b-4688-ae85-46167659bf00'
    obj_destructable_tape_big_walltape01 = 'ed8cb110-bf48-43f6-9e86-273cfc0a7080'
    obj_survivalobject_dispenserbot_spawner = 'eed5ea94-2b85-4c1d-881d-7e07574480f9'
    obj_harvests_trees_leafy03_p00 = 'ef7115ea-a497-4a4a-a1ec-44b810094ef1'
    Drivers_Seat_2 = 'efbf45f8-62ec-4541-9eb1-d529966f6a29'
    Banner = 'efd779ef-ce99-4507-bafb-9e2c7ff8a46c'
    Fridge = 'f08d772f-9851-400f-a014-d847900458a7'
    Plunger = 'f092e8b5-4b10-48be-8ad1-2ac5625f49b8'
    Circuit_Board = 'f152e4df-bc40-44fb-8d20-3b3ff70cdfe3'
    obj_spaceship_corner01 = 'f15b5fa7-6113-4af8-b3e1-b05560ed946a'
    Small_Steel_Bracket = 'f1831414-735f-4323-834a-85d5953fc160'
    Off_Road_Suspension_1 = 'f3cfef9d-faef-4be8-9283-476eb99614d7'
    Emergency_Banana_Box = 'f47612db-e035-4d62-81e2-64fc3453ccc3'
    Orange = 'f5098301-1693-457b-8efc-83b3504105ac'
    Produce_Billboard = 'f5670a5a-7782-4683-bed0-a6eda785a5e2'
    Industrial_Beam_End = 'f5b5acb3-afd5-4755-a7fe-2151f0559d43'
    obj_harvests_trees_leafy02_p00 = 'f708c190-6155-4769-ae0e-884cc8c21300'
    Chemicals = 'f74c2891-79a9-45e0-982e-4896651c2e25'
    Tree_Crate = 'f8b984da-4b24-4e36-b440-86ead126b6dc'
    Unfolded_Onion_Box = 'f8da6b41-03d7-4bc1-ba94-011a351b1569'
    Wood = 'f99ebc34-4821-4b39-a625-b839c5802ed5'
    obj_harvests_trees_pine01_p11 = 'f9a71b9b-d872-4097-863c-a11783642221'
    Woc_Steak = 'fb0f128c-e607-4c52-9c25-f44dfd2dd95e'
    Metal_Storage_Handle = 'fba945c7-a50f-4515-af38-57d768706078'
    obj_harvests_trees_leafy03_p09 = 'fbc59ea5-993f-48a7-8b49-c1cdf67f75e2'
    obj_spaceship_floor_panel = 'fc4f1fd8-2544-45f0-8e3b-4684bc45e5f9'
    Beeswax = 'fcf0958c-084d-4854-9b1b-b06594b4262a'
    Chest = 'fcfae5e2-1df9-47d8-bb9a-30bec9b5b1f5'
    obj_harvests_trees_leafy01_p01 = 'fd381577-bcd2-4b72-b86c-de47d7783820'
    obj_harvests_trees_pine01_p00 = 'fe1d102e-992a-4a24-a942-5fb37e8879d3'
    Corn = 'fe8bfeba-850b-4827-9785-10e2468c9c23'
    Key_Reader = 'ff09d816-843a-43e9-aab6-dc35e73787fd'
    obj_harvests_trees_pine02_p01 = 'ff5bee6a-81a3-49ba-a4b7-d94dbd4b8519'
    Drivers_Seat_5 = 'ffa3a47e-fc0d-4977-802f-bd15683bbe5c'
    Base_Extension = 'fff76292-79aa-4f0d-814f-72e51159d6d7'
    Spaceship_Block = '027bd4ec-b16d-47d2-8756-e18dc2af3eb6'
    Brick_Block = '0603b36e-0bdb-4828-b90c-ff19abcdfe34'
    Path_Light_Block = '073f92af-f37e-4aff-96b3-d66284d5081c'
    Barrier_Block = '09ca2713-28ee-4119-9622-e85490034758'
    Net_Fence = '2228cef0-f22a-4901-93c5-48e4df52caf6'
    Glass_Block = '5f41af56-df4c-4837-9b3c-10781335757f'
    Glass_Tile_Block = '749f69e0-56c9-488c-adf6-66c58531818f'
    Metal_Block_1 = '8aedf6c2-94e1-4506-89d4-a0227c552f1e'
    Tile_Block = '8ca49bff-eeef-4b43-abd0-b527a567f1b7'
    Concrete_Block_1 = 'a6c6ce30-dd47-4587-b475-085d55c6a3b4'
    Wood_Block_1 = 'df953d9c-234f-4ac2-af5e-f0490b223e71'
    Cardboard_Block = 'f0cba95b-2dc4-4492-8fd9-36546a4cb5aa'
    Wood_Block_3 = '061b5d4b-0a6a-4212-b0ae-9e9681f1cbfb'
    Metal_Block_2 = '1016cafc-9f6b-40c9-8713-9019d399783f'
    Wood_Block_2 = '1897ee42-0291-43e4-9645-8c5a5d310398'
    Scrap_Metal_Block = '1f7ac0bb-ad45-4246-9817-59bdf7f7ab39'
    Scrap_Wood_Block = '1fc74a28-addb-451a-878d-c3c605d63811'
    Rusted_Metal_Block = '220b201e-aa40-4995-96c8-e6007af160de'
    Extruded_Metal_Block = '25a5ffe7-11b1-4d3e-8d7a-48129cbaf05e'
    Scrap_Stone_Block = '30a2288b-e88e-4a92-a916-1edbfc2b2dac'
    Solid_Net_Block = '3d0b7a6e-5b40-474c-bbaf-efaa54890e6a'
    Aluminum_Block = '3e3242e4-1791-4f70-8d1d-0ae9ba3ee94c'
    Net_Block = '4aa2a6f0-65a4-42e3-bf96-7dec62570e0b'
    Spaceship_Floor_Block = '4ad97d49-c8a5-47f3-ace3-d56ba3affe50'
    Plastic_Block = '628b2d61-5ceb-43e9-8334-a4135566df7a'
    Restroom_Block = '920b40c8-6dfc-42e7-84e1-d7e7e73128f6'
    Insulation_Block = '9be6047c-3d44-44db-b4b9-9bcf8a9aab20'
    Striped_Net_Block = 'a479066d-4b03-46b5-8437-e99fec3f43ee'
    Concrete_Block_Mould = 'b0329961-7ac0-4a83-aabc-6701e516de7b'
    Plaster_Block = 'b145d9ae-4966-4af6-9497-8fca33f9aee3'
    Square_Mesh_Block = 'b4fa180c-2111-4339-b6fd-aed900b57093'
    Armored_Glass_Block = 'b5ee5539-75a2-4fef-873b-ef7c9398b3f5'
    Crane_Hook_Block = 'b7cf1762-4010-4915-813d-dfbefb100ef5'
    Metal_Block_3 = 'c0dfdea5-a39d-433a-b94a-299345a5df46'
    Framework_Block = 'c4a2ffa8-c245-41fb-9496-966c6ee4648b'
    Sand_Block = 'c56700d9-bbe5-4b17-95ed-cef05bd8be1b'
    Concrete_Slab_Block = 'cd0eff89-b693-40ee-bd4c-3500b23df44e'
    Worn_Metal_Block = 'd740a27d-cc0f-4866-9e07-6a5c516ad719'
    Concrete_Block_3 = 'e281599c-2343-4c86-886e-b2c1444e8810'
    Painted_Wall_Block = 'e981c337-1c8a-449c-8602-1dd990cbba3a'
    Punched_Steel_Block = 'ea6864db-bb4f-4a89-b9ec-977849b6713a'
    Bubble_Plastic_Block = 'f406bf6e-9fd5-4aa0-97c1-0b3c2118198e'
    Cracked_Concrete_Block = 'f5ceb7e3-5576-41d2-82d2-29860cf6e20e'
    Diamond_Plate_Block = 'f7d4bfed-1093-49b9-be32-394c872a1ef4'
    Carpet_Block = 'febce8a6-6c05-4e5d-803b-dfa930286944'
    Concrete_Block_2 = 'ff234e42-5da4-43cc-8893-940547c97882'
    SHAPEID_TO_CLASS = {}
    JOINT_TO_CLASS = {}


class BLOCKS:
    """Block names.
    """
    Spaceship_Block = "Spaceship_Block"
    Brick_Block = "Brick_Block"
    Path_Light_Block = "Path_Light_Block"
    Barrier_Block = "Barrier_Block"
    Net_Fence = "Net_Fence"
    Glass_Block = "Glass_Block"
    Glass_Tile_Block = "Glass_Tile_Block"
    Metal_Block_1 = "Metal_Block_1"
    Tile_Block = "Tile_Block"
    Concrete_Block_1 = "Concrete_Block_1"
    Wood_Block_1 = "Wood_Block_1"
    Cardboard_Block = "Cardboard_Block"
    Wood_Block_3 = "Wood_Block_3"
    Metal_Block_2 = "Metal_Block_2"
    Wood_Block_2 = "Wood_Block_2"
    Scrap_Metal_Block = "Scrap_Metal_Block"
    Scrap_Wood_Block = "Scrap_Wood_Block"
    Rusted_Metal_Block = "Rusted_Metal_Block"
    Extruded_Metal_Block = "Extruded_Metal_Block"
    Scrap_Stone_Block = "Scrap_Stone_Block"
    Solid_Net_Block = "Solid_Net_Block"
    Aluminum_Block = "Aluminum_Block"
    Net_Block = "Net_Block"
    Spaceship_Floor_Block = "Spaceship_Floor_Block"
    Plastic_Block = "Plastic_Block"
    Restroom_Block = "Restroom_Block"
    Insulation_Block = "Insulation_Block"
    Striped_Net_Block = "Striped_Net_Block"
    Concrete_Block_Mould = "Concrete_Block_Mould"
    Plaster_Block = "Plaster_Block"
    Square_Mesh_Block = "Square_Mesh_Block"
    Armored_Glass_Block = "Armored_Glass_Block"
    Crane_Hook_Block = "Crane_Hook_Block"
    Metal_Block_3 = "Metal_Block_3"
    Framework_Block = "Framework_Block"
    Sand_Block = "Sand_Block"
    Concrete_Slab_Block = "Concrete_Slab_Block"
    Worn_Metal_Block = "Worn_Metal_Block"
    Concrete_Block_3 = "Concrete_Block_3"
    Painted_Wall_Block = "Painted_Wall_Block"
    Punched_Steel_Block = "Punched_Steel_Block"
    Bubble_Plastic_Block = "Bubble_Plastic_Block"
    Cracked_Concrete_Block = "Cracked_Concrete_Block"
    Diamond_Plate_Block = "Diamond_Plate_Block"
    Carpet_Block = "Carpet_Block"
    Concrete_Block_2 = "Concrete_Block_2"

class PAINT_COLOR:
    Soft_Peach = "eeeeee"
    White = "eeeeee"
    Medium_Grey = "7f7f7f"
    Light_Grey = "7f7f7f"
    Black_Cow = "4a4a4a"
    Dark_Grey = "4a4a4a"
    Dark_Jungle_Green = "222222"
    Black = "222222"

    Light_Yellow = "f5f071"
    Sandy_Yellow = "f5f071"
    Barberry = "e2db13"
    Yellow = "e2db13"
    Dark_Yellow = "Swamp Green"
    Dark_Yellow = "817c00"
    Woodrush = "323000"
    Aged_Lithium_Grease = "323000"

    Pale_Lime = "cbf66f"
    Yellowish_Green = "a0ea00"
    Murky_Green = "577d07"
    Dark_Olive_Green = "375000"

    Dragon_Green = "68ff88"
    Light_Green = "68ff88"
    Malachite = "19e753"
    Green = "19e753"
    La_Salle_Green = "0e8031"
    Dark_Green = "0e8031"
    Zucchini = "064023"
    Darkest_Green = "064023"

    Blue_Lagoon = "7eeded"
    Blue_Diamond = "2ce6e6"
    Blue_Chill = "118787"
    Rich_Black = "0a4444"

    Ultramarine_Blue = "4c6fe3"
    Light_Blue = "4c6fe3"
    Palatinate_Blue = "0a3ee2"
    Blue = "0a3ee2"
    Smalt = "0f2e91"
    Dark_Blue = "0f2e91"
    Downriver = "0a1d5a"
    Darkest_Blue = "0a1d5a"

    Light_Purple = "ae79f0"
    Purplish_Blue = "7514ed"
    Purple = "7514ed"
    Daisy_Bush = "500aa6"
    Dark_Purple = "500aa6"
    Persian_Indigo = "35086c"
    Darkest_Purple = "35086c"

    Violet = "ee7bf0"
    Hot_Purple = "cf11d2"
    Rich_Purple = "720a74"
    Deep_Violet = "520653"

    Light_Carmine_Pink = "f06767"
    Light_Red = "f06767"
    Fire_Engine_Red = "d02525"
    Red = "d02525"
    Dark_Red = "7c0000"
    Dried_Blood = "560202"
    Darkest_Red = "560202"

    Pale_Orange = "eeaf5c"
    Light_Orange = "eeaf5c"
    Tahiti_Gold = "df7f00"
    Orange = "df7f00"
    Nutmeg_Wood = "673b00"
    Brown = "673b00"
    Deep_Bronze = "472800"
    Dark_Brown = "472800"


class BLOCK_COLOR:
    """Color constants for Blocks and Parts.
    """
    TEMP = "TEMP"
    DEFAULT = "DF7F01"
    DEFAULT_BARRIER_BLOCK = "CE9E0C"
    DEFAULT_BUTTON = "DF7F01"
    DEFAULT_LOGIC_GATE = "DF7F01"
    DEFAULT_SENSOR5 = "DF7F01"
    DEFAULT_SWITCH = "DF7F01"
    DEFAULT_TIMER = "DF7F01"

    Steel_Pallet = Stone_Crate = Metal_Storage_Floor = Metal_Storage_Corner_A = Hay_Crate = Tree_Crate = '902513'
    Duct_Long = Duct_Join = Duct_Short = Duct_Holder = Duct_Corner = Duct_End = 'a4b3b7'
    Mountable_Spud_Gun = Controller = Button = Saddle = Drivers_Saddle = Seat = Bearing = Thruster = Electric_Engine = Wheel = Switch = \
        Horn = Timer = Logic_Gate = Sensor = Drivers_Seat = Gas_Engine = Big_Wheel = Radio = Headlight = Off_Road_Suspension_2 = \
        obj_survivalobject_elevatordoor_left = Electric_Engine_2 = Controller_2 = Generator_Pipe_Tee = Gas_Engine_1 = Craftbot = Sensor_1 = \
        Sensor_5 = Electric_Engine_5 = Controller_4 = Drill = Cookbot = Seat_2 = Saddle_1 = Piston_5 = Gas_Engine_5 = Piston_2 = Gas_Engine_2 = \
        Trigger_Frame = Seat_1 = Saw_Blade = Drivers_Saddle_4 = Saddle_5 = Piston_3 = Seat_4 = Gas_Engine_3 = Thruster_3 = Off_Road_Suspension_4 = \
        Sport_Suspension_5 = Component_Kit = Electric_Engine_3 = Vacuum_Pipe_Corner = Controller_1 = Vacuum_Pipe_1 = Calendar = Refinebot = Electric_Engine_4 = \
        Electric_Engine_1 = Sport_Suspension_1 = Drivers_Saddle_3 = Controller_3 = Seat_5 = Piston_4 = Off_Road_Suspension_5 = Vacuum_Pipe_5 = Saddle_4 = \
        Dressbot = Drivers_Seat_1 = Saddle_3 = Ruin_Chest = Drivers_Saddle_1 = Generator_Pipe_Long = Generator_Pipe_Corner = Generator_Pipe_Short = \
        Piston_1 = Sensor_3 = Vacuum_Pump = obj_survivalobject_cardreader_arm = Vacuum_Pipe = Drivers_Saddle_5 = Thruster_2 = Controller_5 = \
        Elevator_Button = Beacon = Thruster_5 = Vacuum_Pipe_2 = Resource_Collector = Off_Road_Suspension_3 = Sport_Suspension_2 = Large_Chest = \
        Drivers_Saddle_2 = Scrap_Drivers_Seat = Vacuum_Pipe_4 = Gas_Engine_4 = Saddle_2 = Drivers_Seat_3 = Elevator_Lamp = Generator_Pipe_Four_Way = \
        Sensor_2 = Sport_Suspension_3 = Drivers_Seat_4 = Sport_Suspension_4 = Sensor_4 = Woc_Crate = Thruster_1 = Thruster_4 = Warehouse_Wall_Light = \
        Seat_3 = Drivers_Seat_2 = Off_Road_Suspension_1 = Beeswax = Chest = Key_Reader = Drivers_Seat_5 = 'df7f01'
    Valve = 'a41717'
    Wires_Long = Wires_Bend = Wires_Short = Wires_Concave_Bend = Wires_Convex_Bend = '2b3f70'
    Stop_Sign = Beware_Farmbots_Sign = Do_Not_Enter_Sign = 'c60000'
    Pipe_Long = Pipe_Join = Pipe_Short = Paint_Ammo = Corn = '1c8687'
    Large_Pipe_Join = Large_Pipe_Corner = Large_Pipe_Long = Large_Pipe_Short = Large_Pipe_Extension = Large_Pipe_Compressor = Large_Pipe_Cap = \
        Holder_Support_Leg_Base = Large_Pipe_Mount = Holder_Support_Leg = Holder_Support_Bend = 'b42119'
    Ventilation_Grid = Large_Support_Structure = Small_Support_Structure = Support_Structure = U_Beam = Fuse_Box = Metal_Column = Metal_Window = \
        Metal_Support = Corner_Brace = Fan_Blade_Cap = Fan_Base = obj_survivalobject_elevatorfloor = Encryptor_Base_Plate = Small_Steel_Bracket = Base_Extension = '79859c'
    Small_Pipe_Short = Small_Pipe_Corner = Small_Pipe_Four_Way = Small_Pipe_Four_Way_Tee = Small_Pipe_Bend = Small_Pipe_Long = Small_Pipe_Six_Way = \
        Small_Pipe_Five_Way = Small_Pipe_Tee = '7a7a7a'
    Open_Plant_Container = Large_Tank = Medium_Tank = Plant_Container = Steel_Support_Bracket = Unfolded_Grow_Box = '73adb7'
    Woc_Capsule = 'f088b3'
    Air_Conditioner = Bathtub = Sink = Mug = Toilet = obj_spaceship_wall04 = Warehouse_sink = Warehouse_Crate = Ship_Blinds = Master_Battery_Info_Board = \
        obj_spaceship_wall06 = Ship_Ventilation_Panel = Cotton = obj_spaceship_wall02 = obj_spaceship_corner01_damaged = obj_spaceship_wall03 = \
        Bathroom_Stall_Door = Pizza_Burger = Ship_Wall_Panel_Small = obj_spaceship_wall08_damaged = Respawn_Bed = Ship_Ceiling_Ventilation = \
        Ship_Wiring_Short = Water_Cannon = Ship_Wall_Panel_Medium = Water = obj_spaceship_corner03 = obj_spaceship_corner02 = Ship_Wall_Panel_Large = \
        obj_spaceship_wall01 = Bed = obj_spaceship_wall02_damaged = Locker = Broken_Microwave = Ship_Wiring_End = Revival_Baguette = Ship_Wiring_Long = \
        Fridge = obj_spaceship_corner01 = '3e9ffe'
    Grass_Container = 'dadac9'
    Totebot_Head_Bass = '1a538c'
    Banana_Box = Banana_Crate = Banana_Seed = Unfolded_Banana_Box = '83a633'
    Exit_Sign = '14d81e'
    Totebot_Head_Blip = Green_Totebot_Capsule = '49642d'
    Satellite_Dish = Reflector_Antenna = Satellite_Reflector_Dish = Tower_Pole_Top = Antenna = Tower_Pole = Ship_Compartment = Ship_Ventilation = Ship_Shelf = \
        Ship_Dual_fan = '930000'
    I_Beam_Holder = I_Beam_Corner = Long_I_Beam = Short_I_Beam = I_Beam_End = 'f3871c'
    Staircase_Baluster = Staircase_Railing_Join = Staircase_Ramp = Warehouse_Spotlight = Staircase_Short_Railing = Staircase_Long_Railing = Staircase_Banister = \
        Staircase_Landing = Staircase_Wedge = Staircase_Step = Industrial_Beam_Four_Way = Small_Narrow_Warehouse_Ramp = Frame_Beam_Corner = Packing_Lamp = \
        Crane_Loading_Floor = Power_Generator_Side = Industrial_Beam_Corner = Small_Warehouse_Ramp = Industrial_Beam_Corner_Bend = Sound_Isolation_Large = \
        Crane_Leg = Packing_Table = Crane_Top = Generator_A = Large_Narrow_Warehouse_Ramp = Industrial_Beam_Short = Call_Button = Sound_Isolation_Small_ = \
        Ventilation_Frame = Generator_C = Warehouse_Fluorescent_Light = Large_Warehouse_Ramp = Frame_Beam_Short = Warehouse_Spot_Small = Generator_B = \
        Crane_Panel = Encryptor_Base = Packing_Table_Holder = Industrial_Beam_Long = Frame_Beam_Light = Generator_Pipe_Holder = Generator_D = Encryptor_Sign = \
        Frame_Beam_Long = Fan_Blade = Generator_E = Protector_Anti_Destruction = Crane_Cable_Roll = Pack_Instruction_Sign = Frame_Beam_End = \
        Industrial_Beam_Crossing = Crane_Body = Industrial_Beam_End = Square_Mesh_Block = Crane_Hook_Block = 'c36512'
    Traffic_Cone = obj_construction_signcone_taped = Barrier_Stand = 'f15814'
    Large_Explosive_Canister = Small_Explosive_Canister = Totebot_Head_Synth_Voice = 'cb0a00'
    Tubes_Long = Tubes_Short = Tubes_Join = Tubes_Corner = 'a97700'
    Skull_Sign = Baby_Duck_Statuette = Caution_Sign = Net_Fence = 'ffd504'
    Arrow_Sign = 'f26c23'
    Raft_Shark_Mount = '304352'
    Support_Pillar_Stand = Support_Pillar = '597c8d'
    Tapebot_Capsule = '035cff'
    Totebot_Head_Percussion = 'a9831c'
    Pipe_Corner = '565656'
    Small_Windshield = Square_Window = Small_Rectangular_Window = Large_Rectangular_Window = Large_Windshield = '65caff'
    Red_Tapebot_Capsule = 'ec1919'
    Table_Support = Generator_Coil_Corner = Generator_Coil_Segment = '909090'
    Construction_Zone_Sign = Falling_Objects_Sign = Welcome_Sign = 'ffc605'
    Glowbug_Capsule = '92f00f'
    Big_Pot = Potted_Seed_Plant = 'af4200'
    Beetroot_Box = 'c57246'
    Vegetable_Box = '7d9f2b'
    Small_Potted_Plant = Potted_Vine_Plant = Potted_Plant = 'be6740'
    Fruit_Box = '84dfd2'
    Orange_Box = 'f59d39'
    Shelf_Support = Shelf = Shelf_Pillar = Tall_Shelf_Support = Water_Dispenser = obj_survivalobject_elevatorfan = obj_survivalobject_elevatorceiling = \
        obj_office_waterdispensertank_taped = obj_survivalobject_elevatorwallleft = obj_survivalobject_elevatorwallright = Water_Tank = '408fc7'
    Farmbot_Capsule = 'c52c18'
    Mattress = 'b58d59'
    Danger_Sign = 'ed541b'
    Maintenance_Ship_Door = Small_Ship_Corner_Floor_Mold = Ship_Opening_Floor_Mold = obj_spaceship_wall12_damaged = Ship_Floor_Mold = obj_spaceship_wall12 = \
        obj_spaceship_wall05 = Large_Ship_Corner_Floor_Mold = Large_Ship_Floor_Mold = Diagonal_Ship_Floor_Mold = obj_spaceship_floor_panel = Spaceship_Block = '820a0a'
    Mannequin_Hand = 'e48c71'
    Potted_Blue_Flower = Potted_Cactus = Potted_Blooming_Cactus = '9c251c'
    Wooden_Crate = 'cb8d43'
    Screw = Nut = '59615c'
    Mannequin_Boot = '8d4104'
    Haybot_Capsule = Scrap_Metal = 'e75b0f'
    Onion_Box = Unfolded_Onion_Box = 'bc8543'
    Toilet_Paper = 'e44949'
    Cucumber_Box = 'be4d22'
    Small_Tank = 'cc7f3b'
    Carrot_Box = '62cedc'
    Pillow = '5aa0d2'
    Scrap_Stone = obj_harvest_stonechunk01 = Stand_Support_Corner = obj_harvests_stones_p04 = Stand_Support = obj_harvest_stonechunk03 = obj_harvest_stonechunk02 = \
        Metal = obj_harvests_stones_p05 = obj_harvests_stones_p06 = Stand_Support_A = Stand_Support_Base = obj_harvests_stones_p02 = obj_harvests_stones_p03 = \
        obj_harvests_stones_p01 = Stand_Support_Long = 'ee9e28'
    obj_harvests_trees_pine03_p08 = obj_harvests_trees_pine03_p09 = obj_harvests_trees_birch02_p04 = obj_harvests_trees_birch03_p06 = \
        obj_harvests_trees_birch03_p01 = obj_harvests_trees_birch03_p04 = obj_harvest_log_l02b = obj_harvest_log_m01 = obj_harvests_trees_birch02_p01 = \
        obj_harvests_trees_pine03_p10 = obj_harvests_trees_pine02_p04 = obj_harvests_trees_pine01_p07 = obj_harvests_trees_birch01_p04 = \
        obj_harvests_trees_birch03_p03 = obj_harvests_trees_birch01_p01 = obj_harvests_trees_pine01_p10 = obj_harvests_trees_pine01_p08 = \
        obj_harvests_trees_birch02_p06 = obj_harvest_log_l02a = obj_harvests_trees_pine03_p05 = obj_harvests_trees_leafy01_p00 = \
        obj_harvests_trees_pine02_p00 = obj_harvests_trees_birch02_p03 = obj_harvests_trees_pine03_p07 = obj_harvests_trees_birch01_p00 = \
        obj_harvests_trees_spruce02_p00 = obj_harvests_trees_pine01_p06 = obj_harvests_trees_birch01_p02 = obj_harvests_trees_pine01_p01 = \
        obj_harvests_trees_pine02_p03 = obj_harvests_trees_birch01_p05 = obj_harvests_trees_pine02_p06 = obj_harvests_trees_pine03_p00 = \
        obj_harvests_trees_pine01_p05 = obj_harvests_trees_pine02_p08 = obj_harvests_trees_birch01_p03 = obj_harvests_trees_pine02_p10 = \
        obj_harvests_trees_pine03_p04 = obj_harvest_log_s01 = obj_harvests_trees_birch02_p00 = obj_harvests_trees_pine03_p01 = obj_harvests_trees_pine03_p06 = \
        obj_harvests_trees_pine01_p02 = obj_harvests_trees_pine02_p02 = Scrap_Wood = obj_harvests_trees_pine03_p02 = obj_harvest_log_l01 = \
        obj_harvests_trees_birch03_p02 = obj_harvests_trees_pine02_p05 = obj_harvests_trees_pine02_p07 = obj_harvests_trees_birch03_p00 = \
        obj_harvests_trees_pine01_p09 = obj_harvests_trees_pine01_p03 = obj_harvests_trees_pine02_p09 = obj_harvests_trees_birch02_p02 = \
        obj_harvests_trees_birch03_p05 = obj_harvests_trees_birch02_p05 = obj_harvests_trees_pine03_p03 = obj_harvests_trees_pine01_p04 = \
        obj_harvests_trees_leafy03_p00 = obj_harvests_trees_leafy02_p00 = Wood = obj_harvests_trees_pine01_p11 = obj_harvests_trees_pine01_p00 = \
        obj_harvests_trees_pine02_p01 = '7b7f10ff'
    Gas_Container = 'c52319'
    Giant_Pipe_Glass_Straight = Giant_Pipe_Glass_Corner = Elevator_Sign = Giant_Pipe_Corner = Warehouse_Sign = Giant_Pipe = Office_Sign = Giant_Pipe_Tee = \
        Utility_Sign = Packing_Sign = Storage_Sign = 'd07500'
    Berry_Billboard = Sickle_Down_Billboard = Produce_Billboard = '4f4f4f'
    Scaffold_Frame = Mop_Set = Scaffold_Pallet_Ramp = Scaffold_Ledger = Carpet_Spool_Holder = Slippery_Surface_Sign = Work_Light = Paint_Bucket = \
        Scaffolding_Step = Construction_Pallet = 'ebb100'
    Potato_Ammo_Container = Potato = '505c30'
    Shack_Roof = '3a5964'
    Carpet_Roll = Carpet_Block = '368085'
    Encryptor_Holder = Warehouse_Ventilation_Mount = Encryptor_Frame_Beam = Warehouse_Ventilation_Long = Warehouse_Ventilation_Short = \
        Warehouse_Ventilation_Corner = Warehouse_Ventilation_Drum = Warehouse_Ventilation_Tee = 'a2a2a2'
    Broken_Concrete_Large = Broken_Concrete_Medium = Broken_Concrete_Small = Concrete_Block_1 = Cracked_Concrete_Block = Concrete_Block_2 = '8d8f89'
    Water_Bucket = Chemical_Bucket = Plastic_Block = '0b9ade'
    obj_destructable_tape_acrosstheroom02 = obj_destructable_tape_taperoll04 = obj_destructable_tape_tape06 = obj_destructable_tape_rooftape04 = \
        obj_destructable_tape_tape02 = obj_destructable_tape_corridor01 = obj_destructable_tape_big_walltape04 = obj_destructable_tape_cocoon02 = \
        obj_destructable_tape_rooftape03 = obj_destructable_tape_tape05 = obj_destructable_tape_cornertape01 = obj_destructable_tape_doorwaytape01_destroyed = \
        obj_destructable_tape_cornertape02 = obj_destructable_tape_rooftape01 = obj_destructable_tape_cornertape03 = obj_destructable_tape_tape04 = \
        obj_destructable_tape_tape03 = obj_destructable_tape_doorwaytape01 = obj_destructable_tape_corridor02 = obj_destructable_tape_acrosstheroom03 = \
        obj_destructable_tape_rooftape02 = obj_destructable_tape_corridor03 = obj_destructable_tape_cocoon01 = obj_destructable_tape_taperoll03 = \
        obj_destructable_tape_taperoll01 = obj_destructable_tape_taperoll02 = obj_destructable_tape_tape01 = obj_destructable_tape_cornertape04 = \
        obj_destructable_tape_big_walltape03 = obj_destructable_tape_acrosstheroom01 = obj_destructable_tape_big_walltape02 = obj_destructable_tape_big_walltape05 = \
        obj_destructable_tape_big_walltape01 = 'ffea00'
    Crude_Oil = Chemical_Container = Chemicals = '495975'
    obj_tool_handbook = Framework_Block = "0F0F0F"
    Office_Table_A = Office_Chair_Base = Office_Table_Leg = Office_Table_B = Office_Chair_Top = Cubicle_Wall = obj_office_officechair_taped = '8c9c3f'
    Hollow_Concrete = '82847e'
    Broccoli_Seed = Broccoli_Crate = '7c862c'
    Tomato_Crate = Tomato_Seed = obj_packingstation_crateload = 'e39c04'
    Ship_Floor_Tile = Handle = 'a1a1a1'
    Large_Taperoll = 'ffa000'
    Hard_Work_Sign = 'eb6a90'
    Man_Sign = Old_Restroom_Mirror = Woman_Sign = '3495e8'
    Sale_Sign = 'e9e9e9'
    Cup_Holder = 'b43320'
    Haystack = Hay_Bale = '0a956d'
    Ember = Rounded_Frame_Corner = License_Plate = Metallic_Tube_Straight = Metallic_Tube_Bend = '808080'
    Garment_Box_Rare = 'a20fff'
    Fresh_Neon_Sign = '19f088'
    Shack_Wall = Shack_Half_Wall = '0a4444'
    Metal_Storage_Corner_C = Metal_Storage_Handle = '77777c'
    Woc_Milk = obj_tool_spudgun = obj_tool_frier = obj_hideout_questgiver = obj_tool_paint = obj_tool_weld = obj_tool_connect = obj_tool_spudling = 'ffffff'
    Warehouse_Brick_Lamp = 'ffc27a'
    Mini_Craftbot = Crane_Hook = Master_Battery_Socket = Master_Battery = obj_survivalobject_dispenserbot = Ship_Terminal = \
        obj_survivalobject_dispenserbot_spawner = '4a4a4a'
    obj_harvests_trees_spruce02_p02 = obj_harvests_trees_spruce02_p05 = obj_harvests_trees_leafy03_p01 = obj_harvests_trees_leafy02_p04 = \
        obj_harvests_trees_leafy03_p02 = obj_harvests_trees_leafy02_p03 = obj_harvests_trees_leafy03_p06 = obj_harvests_trees_leafy02_p06 = \
        obj_harvests_trees_leafy02_p02 = obj_harvests_trees_leafy03_p04 = obj_harvests_trees_leafy03_p03 = obj_harvests_trees_leafy01_p04 = \
        obj_harvests_trees_spruce03_p05 = obj_harvests_trees_leafy01_p03 = obj_harvests_trees_leafy03_p05 = obj_harvests_trees_leafy02_p05 = \
        obj_harvests_trees_leafy03_p08 = obj_harvests_trees_spruce02_p04 = obj_harvests_trees_leafy02_p07 = obj_harvests_trees_spruce02_p01 = \
        obj_harvests_trees_spruce01_p05 = obj_harvests_trees_leafy02_p01 = obj_harvests_trees_leafy03_p07 = obj_harvests_trees_leafy01_p02 = \
        obj_harvests_trees_spruce02_p03 = obj_harvests_trees_leafy03_p09 = obj_harvests_trees_leafy01_p01 = '7b7f10ff'
    Cash_Register = Open_Sign = '005952'
    Net_frame = Net_frame_hatch = Barrier_Block = 'ce9e0c'
    Glue = '3da851'
    Glow = Pigment_Flower = Circuit_Board = Woc_Steak = '4bffb5'
    Seed_Container = '4c9938'
    Glowstick = Veggie_Burger = 'ccffcc'
    Encryptor_Frame_Top = 'ebb600'
    Power_Station = '0d7308'
    Glue_Clam = 'aaa8ef'
    Metal_Storage_Support = '999999'
    Ship_Light = 'df9a16'
    Carrot = 'ef650b'
    Blueberry_Seed = Blueberry_Crate = '5d41d9'
    Redbeet = 'a6274d'
    Pineapple = 'e9ec0e'
    obj_packingstation_mid = obj_packingstation_screen_veggie = obj_packingstation_front = obj_packingstation_screen_fruit = 'c8e6ff'
    Scrap_Wheel = '9f5223'
    Sunshake_Vending_Machine = Udder_Decoration = 'fc949d'
    Warehouse_Square_Light = Painted_Wall_Block = 'eeeeee'
    Cement_Mix = Concrete_Block_Mould = '50612d'
    Redbeet_Crate = Redbeet_Seed = 'a42039'
    Garment_Box_Common = '19e753'
    Metal_Storage_Ramp = Large_Metal_Storage_Lamp = Metal_Storage_Corner_B = Metal_Storage_Beam = '5f5f5f'
    Giant_Pipe_Holder = 'c20000'
    Generator_Tank = '529374'
    Blueberry = '032ea8'
    Banner_Holder = Crane_Wheel = Banner = '8a0000'
    Tomato = 'f80600'
    Concave_Wedge = '518d3c'
    Hideout_Button = Caged_Farmer = obj_hideout_dropoff = '9f2600'
    Wrapping_Roll = '6de5ff'
    Old_Fruit_Stand = Stacked_Crates = '5f7514'
    Fertilizer_Container = '357a1b'
    Garment_Box_Epic = 'f9b303'
    Road_Sign_Base = Traffic_Sign = Metallic_Tube = '323232'
    Blueberry_Juice_Cylinder = '655dd5'
    Scaffold_Plastic_Wall = '1999eb'
    Small_Taperolls = 'ffb400'
    Scrap_Seat = Scrap_Gas_Engine = '2f7847'
    Oily_Toilet_Seat = 'd37676'
    Scaffold_Plank = '3a3a40'
    Encryptor_Anti_Connection = '2f97df'
    File_Cabinet = 'beb16c'
    Battery = Battery_Container = 'f1a400'
    Cotton_Seed = 'ff72bb'
    Giant_Pipe_Bracer = '555e68'
    Soil_Bag = '3a9c51'
    Carrot_Seed = Carrot_Crate = '3f7abc'
    Pineapple_Seed = Pineapple_Crate = '23b777'
    Tomato_Juice_Cylinder = 'd33520'
    Banana = 'f0c909'
    Fertilizer = 'a5ca11'
    Broccoli = '31880b'
    Master_Switch = '9f1515'
    Orange_Seed = Orange_Crate = 'fd5d38'
    Shack_Awning = Shack_Shade_Sails = '0e8031'
    Sunshake = 'fe878c'
    Protector_Sign = '4c6fe3'
    Recycling_Bin = 'c8c628'
    Main_Humidifier = Gasoline = '981e11'
    Paper_Stack = 'd2c6af'
    K_O__Bag = Warehouse_Key = 'cbcbcb'
    Capsule_Door = '3ca3f0'
    Water_Container = '008ae1'
    Potato_Seed = '52662e'
    Shack_Light = 'e17f51'
    Plunger = '9a3535'
    Emergency_Banana_Box = 'c48c13'
    Orange = 'ffad1f'
    Brick_Block = Concrete_Slab_Block = 'af967b'
    Path_Light_Block = Aluminum_Block = '727272'
    Glass_Block = 'e4f8ff'
    Glass_Tile_Block = 'c2f9ff'
    Metal_Block_1 = '675f51'
    Tile_Block = 'bfdfed'
    Wood_Block_1 = '9b683a'
    Cardboard_Block = 'a48052'
    Wood_Block_3 = 'f2ad74'
    Metal_Block_2 = '869499'
    Wood_Block_2 = 'dc9153'
    Scrap_Metal_Block = 'df6226'
    Scrap_Wood_Block = 'cd9d71'
    Rusted_Metal_Block = '738192'
    Extruded_Metal_Block = '858795'
    Scrap_Stone_Block = '848484'
    Solid_Net_Block = Striped_Net_Block = Punched_Steel_Block = '888888'
    Net_Block = '435359'
    Spaceship_Floor_Block = 'dadada'
    Restroom_Block = '607b79'
    Insulation_Block = 'fff063'
    Plaster_Block = '979797'
    Armored_Glass_Block = '3abfb1'
    Metal_Block_3 = '88a5ac'
    Sand_Block = 'c69146'
    Worn_Metal_Block = '66837c'
    Concrete_Block_3 = 'c9d7dc'
    Bubble_Plastic_Block = '9acfd2'
    Diamond_Plate_Block = '43494d'


class AXIS:
    """Default axises
    """
    DEFAULT_XAXIS = 1
    DEFAULT_ZAXIS = 3
    DEFAULT_XAXIS_INTERACTABLE = 2
    DEFAULT_ZAXIS_INTERACTABLE = 1


class ROTATION:
    """Rotations constants ( by @Inventorsteve :) )
    """
    FACING = Literal["west", "up", "down", "south", "north", "east"]
    ROTATED = Literal["down", "right", "left", "up"]
    ROTATION_TABLE = {
        "west": {"down": (1, 0, 0, 2, 3), "right": (1, 1, 0, 3, -2), "left": (1, 0, 1, -3, 2), "up": (1, 1, 1, -2, -3)},
        "up": {"down": (1, 1, 0, -2, -1), "right": (0, 1, 0, 1, -2), "left": (1, 0, 0, -1, 2), "up": (0, 0, 0, 2, 1)},
        "down": {"down": (1, 1, 1, -1, -2), "right": (1, 0, 1, 2, -1), "left": (0, 1, 1, -2, 1), "up": (0, 0, 1, 1, 2)},
        "south": {"down": (1, 1, 0, -1, 3), "right": (0, 1, 0, 3, 1), "left": (1, 1, 1, -3, -1),"up": (0, 1, 1, 1, -3)},
        "north": {"down": (0, 0, 0, 1, 3), "right": (1, 0, 0, 3, -1), "left": (0, 0, 1, -3, 1),"up": (1, 0, 1, -1, -3)},
        "east": {"down": (0, 1, 0, 2, 3), "right": (0, 0, 0, 3, 2), "left": (0, 1, 1, -3, -2), "up": (0, 0, 1, 2, -3)}}


class VERSION:
    """Blueprint version
    """
    BLUEPRINT_VERSION = 4


TICKS_PER_SECOND = 40

__global_id_counter = 0
"""Atempting to modify this global variable may cause to break your blueprints lol.
"""


def get_new_id():
    """Get a unique ID (incremental)

    Returns:
        int: The unique ID.
    """
    global __global_id_counter
    __global_id_counter = (new_id := __global_id_counter) + 1
    return new_id

def get_current_id():
    """returns the current ID

    Returns:
        int: The unique ID.
    """
    global __global_id_counter
    __global_id_counter = (ID := __global_id_counter)
    return ID-1
