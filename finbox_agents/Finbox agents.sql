/*
DROP TABLE #GREEN_FIELDS
DROP TABLE #YELLOW_FIELDS
DROP TABLE #NUM_OF_AGENTS
DROP TABLE #MAIN_WO_REPEATS
DROP TABLE #DELIVERIES
DROP TABLE #REQUESTS
DROP TABLE #ACTIVATIONS
DROP TABLE #STEP_1
DROP TABLE #FINBOX_AGENTS_W_DUPLICATES
DROP TABLE #AGENTS_BOT
*/
--<
   SELECT *
     INTO #GREEN_FIELDS
     FROM OPENQUERY(SRCETL,
'
	 WITH FIS as 
(
   SELECT DISTINCT
		  user_login,
		  user_fio,
		  out_user_id,
		  user_rbs_code,
		  replace(user_passport, '' '', '''') as user_passport
	 FROM psb.fis_halva_user
	WHERE req_type = 59
	  AND is_block = 0
),

          RBS_ID as 
(
   SELECT a1.user_login,
          a1.user_fio,
		  b2.customer_id,
		  b2.CUSTOMER_FIO,
		  b2.customer_birthday,
		  ROW_NUMBER() OVER(PARTITION BY b2.customer_id ORDER BY release_date desc) as r_n
	 FROM PSB.RBS_CARD_full b2 
	 JOIN FIS a1
	   ON a1.user_passport = b2.customer_pass
),

	      LAST_HALVA_PHONE as
(
   SELECT a1.CUSTOMER_ID,
		  b2.user_login,
		  a1.MOBILE_TELEPHONE as HALVA_PHONE,
		  row_number() over(partition by a1.CUSTOMER_ID order by release_date desc) as r_n
	 FROM PSB.RBS_CARD_CUSTOMER_SCC a1 
	 JOIN RBS_ID b2
	   ON a1.customer_id = b2.customer_id
	  AND b2.r_n = 1
	WHERE mobile_telephone is not null
),

          AGENT_PERSONAL_CARD as
(	
   SELECT a1.user_login,
		  b2.id as card_id,
		  case when b2.cred_id is null then b2.dep_id else b2.cred_id end as cred_id,
		  case  
			  when card_status = ''Рабочая'' then ''Рабочая''
			  when card_status = ''Блокирована'' then ''Блокирована''
			  when card_status = ''Архив'' then ''Архив''
		  end as CARD_STATUS,
		  row_number() over(partition by a1.user_login order by 
					                                           case  
							                                       when card_status = ''Рабочая'' then ''Рабочая''
							                                       when card_status = ''Блокирована'' then ''Блокирована''
							                                       when card_status = ''Архив'' then ''Архив''
						                                       end desc,
					                                           case 
						                                           when upper(cred_product_name) like (''%Карта рассрочки "Халва 2.0"%'') or upper(card_product_name) like (''%Халва 4.0 МИР розница (Разрешен 2.0) без физического носителя%'') then 1
						                                           when upper(cred_product_name) like (''%ВОСТОЧН%'') or upper(cred_product_name) like (''%СОВЕСТ%'') or upper(cred_product_name) like (''%ХАЛВА_ХКБ%'') then 2
					                                               else 3
					                                           end desc,
					                                           card_limit desc,						
				                                               RELEASE_DATE desc
	                        ) as r_n
	 FROM RBS_ID a1
	 JOIN PSB.RBS_CARD_CUSTOMER_SCC b2 
	   ON a1.customer_id = b2.customer_id
    WHERE (cred_id is not null OR b2.dep_id is not null)
	  AND a1.r_n = 1
	  AND upper(card_product_name) not like (''%ХАЛВЕНОК%'')
	  AND (card_product_name) not like (''%Халва 4.0 МИР розница (Разрешен 2.0) без физического носителя%'')		
),
	
          OMP as
( 
   SELECT b2.customer_id,
		  max(event_time) as event_time
	 FROM psb.hd_openapi a1
	 JOIN RBS_ID b2
	   ON a1.customer_id = b2.customer_id
	  AND b2.r_n = 1
	WHERE (
	       APP_TYPE = ''ANDROID''
		   OR
		   APP_TYPE = ''IOS''
		  )
	  AND DBO_TYPE = ''OMP''		
 GROUP BY b2.customer_id
),

	      MOP as 
(
   SELECT b2.customer_id,
          MAX(CASE 
				  WHEN trunc(a1.end_date, ''month'') = trunc(current_date - 1, ''month'')
				       AND
					   target_complete = 1
				  THEN 1
				  ELSE 0 
			  END) as curr_5_10,
		  MAX(CASE 
				  WHEN trunc(a1.end_date, ''month'') = trunc(current_date - 1, ''month'') - interval ''1'' month
				       AND
				       target_complete = 1
			      THEN 1
			      ELSE 0 
			  END) as prev_5_10
	 FROM PSB.PV_RBS_HALVA_MOP      a1
	 JOIN PSB.RBS_CARD_CUSTOMER_SCC b2
	   ON CASE WHEN b2.cred_id is null THEN b2.dep_id ELSE b2.cred_id END = a1.cred_id
	 JOIN RBS_ID c3
	   ON b2.customer_id = c3.customer_id
	  AND c3.r_n = 1
 GROUP BY b2.customer_id
),

	      TEN_FULL as
(
   SELECT b2.customer_id,
          max(CASE
		          WHEN date_open < current_date - 1
				       AND
					   date_close >= current_date - 1
				  THEN 1
				  ELSE 0
			  END) as TEN_ACT
     FROM psb.pv_rbs_card_actions a1
	 JOIN RBS_ID b2
	   ON a1.customer_id = b2.customer_id
	WHERE a1.tariff_name = ''Десяточка''
	   OR a1.tariff_name = ''Десяточка (ГП)''
 GROUP BY b2.customer_id
),

	      PAY_OMP as
(
   SELECT b2.customer_id,
          MAX(CASE
		          WHEN sms_date is not null
				  THEN 1
				  ELSE 0
			  END) as omp_flag,
		  MAX(CASE
		          WHEN add_pay is not null 
				  THEN 1
				  ELSE 0
			  END) as pay_flag
	 FROM psb.pv_front_mp_info A1
	 JOIN PSB.RBS_CARD_CUSTOMER_SCC b2
	   ON CASE when b2.cred_id is null THEN b2.dep_id ELSE b2.cred_id END = a1.cred_id
	 JOIN RBS_ID c3
	   ON b2.customer_id = c3.customer_id
	  AND c3.r_n = 1
 GROUP BY b2.customer_id
)

   SELECT a1.OUT_USER_ID,
		  a1.user_passport,
		  b2.HALVA_PHONE,
		  c3.CARD_STATUS,
		  c3.card_id,
		  c3.cred_id,
		  ten.TEN_ACT,
		  case when e5.event_time is not null then ''1'' else ''0'' end as OMP_possession,
		  e5.event_time as last_time_OMP,
		  coalesce(pay.pay_flag, 0) as PAY,
		  mop.curr_5_10,
		  mop.prev_5_10,
		  d4.customer_id
	 FROM FIS a1
LEFT JOIN LAST_HALVA_PHONE b2
	   ON a1.user_login = b2.user_login
	  AND b2.r_n = 1
LEFT JOIN AGENT_PERSONAL_CARD c3
	   ON a1.user_login = c3.user_login
	  AND c3.r_n = 1
LEFT JOIN RBS_ID d4
	   ON a1.user_login = d4.user_login
	  AND d4.r_n = 1
LEFT JOIN OMP e5
	   ON d4.customer_id = e5.customer_id
LEFT JOIN MOP mop
       ON d4.customer_id = mop.customer_id
LEFT JOIN TEN_FULL ten
       ON d4.customer_id = ten.customer_id
LEFT JOIN PAY_OMP pay
       ON d4.customer_id = pay.customer_id
'
)
--<
   SELECT *
     INTO #YELLOW_FIELDS
     FROM OPENQUERY(SRCETL,
'
   SELECT FIS_POINT_ID,
		  inn,
		  brand,
		  group_goods,
		  REPLACE(REPLACE(REPLACE(POINT_ADDRESS, '';'', '',''), '' ('', '', ''), '')'', '''') as POINT_ADDRESS,
		  REPLACE(REPLACE(POINT_ORIG_NAME, '';'', '',''), ''MoneyCare'', ''Finbox'') as POINT_ORIG_NAME,
		  ROW_NUMBER() OVER(PARTITION BY FIS_POINT_ID ORDER BY create_date desc) as r_n
	 FROM psb.fis_halva_org_point
'
) a1
    WHERE r_n = 1
--<
   SELECT *,
          CASE
			  WHEN [Номер телефона] is not null
			  THEN ROW_NUMBER() OVER(partition by [Номер телефона] order by [ID Сотрудника])
	          ELSE ROW_NUMBER() OVER(partition by [ID Сотрудника]  order by [ID Сотрудника])
		  END as r_n -- партнёр направляет пользователей на повторную заливку с новым айди, но айди должен оставаться первый присвоенный; айди работают как числа (поздний как число будет больше раннего)
	 INTO #MAIN_WO_REPEATS
     FROM [TRANSPORT].[dbo].[FINBOX_DATA]
--<
   SELECT [ID ТТ],
          count(DISTINCT [ID Сотрудника]) as num_ags
	 INTO #NUM_OF_AGENTS
     FROM #MAIN_WO_REPEATS
	WHERE r_n = 1
 GROUP BY [ID ТТ]
--<
   SELECT *
     INTO #REQUESTS
	 FROM OPENQUERY(SRCETL,
'
   SELECT fis.OUT_USER_ID,
          count(*) as num_of_reqs	  
     FROM PSB.PV_FRONT_REQ_CRDT req
LEFT JOIN psb.fis_halva_org_point pts
       ON req.rpnt_issue_id = pts.id
LEFT JOIN psb.fis_halva_user fis
       ON req.user_id = fis.id
    WHERE pts.req_type_id = 59
	  AND req.repdate >= date''2023-06-01''
	  AND UPPER(req.crdt_schema) like UPPER(''%Халв%'')
 GROUP BY fis.OUT_USER_ID
'
)
--<
   SELECT *
     INTO #DELIVERIES
	 FROM OPENQUERY(SRCETL,
'
   SELECT fis.OUT_USER_ID,
          count(*) as num_of_delivs
     FROM PSB.PV_FRONT_REQ_CRDT req
LEFT JOIN psb.fis_halva_org_point pts
       ON req.rpnt_issue_id = pts.id
LEFT JOIN psb.fis_halva_user fis
       ON req.user_id = fis.id
    WHERE pts.req_type_id = 59
	  AND req.repdate >= date''2023-06-01''
	  AND UPPER(req.crdt_schema) like UPPER(''%Халв%'')
	  AND req.ISSUE_COMPLETE = 1
 GROUP BY fis.OUT_USER_ID
'
)
--<
   SELECT *
     INTO #ACTIVATIONS
     FROM OPENQUERY(SRCETL,
'
     WITH FINBOX_AGENTS_DELIVS AS
(
   SELECT repdate,
          user_id,
          CRDT_NUMBER,
		  crdt_schema
     FROM PSB.PV_FRONT_REQ_CRDT req
LEFT JOIN psb.fis_halva_org_point pts
       ON req.rpnt_issue_id = pts.id
LEFT JOIN psb.fis_halva_user fis
       ON req.user_id = fis.id
    WHERE pts.req_type_id = 59
	  AND req.repdate >= date''2023-06-01''
	  AND UPPER(req.crdt_schema) like UPPER(''%Халв%'')
	  AND req.ISSUE_COMPLETE = 1
),

          ACTIVATION AS
(
   SELECT opers.OBJID,
          max (
		       CASE
		           WHEN trunc(opers.REPDATE, ''DDD'') = trunc(dlvs.repdate,''DDD'')
				   AND opers.AMOUNT >= 500 
				   THEN 1
				   ELSE 0 
			   END
			   ) as ACTIVATION_FLAG
     FROM PSB.RBS_CARD_OPERATION_FULL opers
	 JOIN FINBOX_AGENTS_DELIVS dlvs
	   ON dlvs.CRDT_NUMBER = opers.OBJID
	  AND trunc(opers.REPDATE, ''DDD'') = trunc(dlvs.repdate, ''DDD'')
	WHERE (
	       opers.TR_TYPE = (''Покупка'')
	       OR
		   WL_MERCHANT_ID = 2652108326
		  )
 GROUP BY opers.OBJID
),

          FINBOX_AGENTS_DELIVS_ACT AS
(
   SELECT dlvs.user_id,
          dlvs.CRDT_NUMBER,
		  case when upper(CRDT_SCHEMA) like upper(''%Спецрассрочка Халва%'') then 1 else act.ACTIVATION_FLAG end as ACTIVATION_FLAG
	 FROM FINBOX_AGENTS_DELIVS dlvs
LEFT JOIN ACTIVATION act
       on dlvs.crdt_number = act.OBJID
)


   SELECT fis.OUT_USER_ID,
          count(*) as num_of_acts
     FROM FINBOX_AGENTS_DELIVS_ACT dlvs_act
LEFT JOIN psb.fis_halva_user fis
       ON dlvs_act.user_id = fis.id
	WHERE ACTIVATION_FLAG = 1
 GROUP BY fis.OUT_USER_ID
'
)
--<
   SELECT OUT_USER_ID,
          RIGHT([Телефон], 10) as telephone,
		  row_number() over(partition by OUT_USER_ID order by cast(b2.load_date as date)) as r_n
     INTO #AGENTS_BOT
     FROM #GREEN_FIELDS a1
LEFT JOIN #MAIN_WO_REPEATS main
       ON a1.OUT_USER_ID = CAST(main.[ID Сотрудника] AS varchar)
LEFT JOIN [TRANSPORT].[dbo].[SPO_TELEGRAM_AGENTS_CURRENT] b2
       ON (RIGHT(b2.[Телефон], 10) = right(main.[Номер телефона], 10)
	   OR RIGHT(b2.[Телефон], 10) = right(a1.HALVA_PHONE, 10))  
    WHERE [Телефон] is not null
	  AND [Дата отключения от бота] is null
	  AND main.r_n = 1
--<
   SELECT main.[ID Сотрудника]  as [ID сотрудника],
		  main.[ФИО Сотрудника] as [ФИО сотрудника],
		  main.[Дата рождения],
		  main.[Место рождения по Паспорту] as [Место рождения по паспорту],
		  main.[Адрес по прописке],
		  CASE
			  WHEN green.user_passport is not null
		      THEN green.user_passport
			  ELSE CONCAT(main.[Серияпаспорта], main.[Номерпаспорта])
		  END as [Паспорт],
		  main.[Код подразделения],
		  main.[Кем выдан],
		  main.[Дата выдачи паспорта],
		  main.[Номер телефона],
		  main.[ID ТТ],
          green.HALVA_PHONE      as [Тел., привязанный к «Халве»],
		  green.CARD_STATUS      as [Статус карты],
	      green.card_id          as [ID карты],
		  green.cred_id          as [Кредитный договор],
		  green.ten_act          as [Наличие «Десятки»],
		  green.OMP_possession   as [Наличие ОМП],
		  green.last_time_OMP    as [Последний вход в ОМП],
		  green.pay              as [Подключение Pay],
		  green.curr_5_10        as [Выполнение 5х10 в текущем ОП],
		  green.prev_5_10        as [Выполнение 5х10 в прошлом ОП],
		  case when bot.OUT_USER_ID IS not null then '1' else '0' end as [Агент в чат-боте],
		  green.customer_id      as [ID RBS агента],
		  CASE WHEN yellow.inn             is not null THEN yellow.inn             ELSE yellow_777.inn             END as [ИНН],
		  CASE WHEN yellow.brand           is not null THEN yellow.brand           ELSE yellow_777.brand           END as [Бренд],
		  CASE WHEN yellow.group_goods     is not null THEN yellow.group_goods     ELSE yellow_777.group_goods     END as [Категория],
		  CASE WHEN yellow.POINT_ADDRESS   is not null THEN yellow.POINT_ADDRESS   ELSE yellow_777.POINT_ADDRESS   END as [Адрес],
		  CASE WHEN yellow.POINT_ORIG_NAME is not null THEN yellow.POINT_ORIG_NAME ELSE yellow_777.POINT_ORIG_NAME END as [ТТ]
	 INTO #STEP_1
     FROM #MAIN_WO_REPEATS main
LEFT JOIN #GREEN_FIELDS green
       ON CAST(main.[ID Сотрудника] AS varchar) = green.OUT_USER_ID
LEFT JOIN #YELLOW_FIELDS yellow
       ON CAST(main.[ID ТТ] as varchar) = yellow.FIS_POINT_ID
LEFT JOIN #YELLOW_FIELDS yellow_777
       ON CONCAT('777', CAST(main.[ID ТТ] as varchar)) = yellow_777.FIS_POINT_ID -- в ФИСе некоторые логины начинаются с 777, Смышялева присылает без них, поэтому нужно это условие, чтобы получить информацию
LEFT JOIN #AGENTS_BOT bot
       ON CAST(main.[ID Сотрудника] AS varchar) = bot.OUT_USER_ID
	  AND bot.r_n = 1
	WHERE main.r_n = 1
--<
   SELECT step1.*,
          num_ags.num_ags     as [К-во агентов на ТТ],
		  spo_base.[Логин агента]     as [Логин СПО],
		  spo_base.[Статус агента DESS],
		  spo_base.[Наименование ТТ (заполняет иниц.) - последняя закрепленная точка за агентом на формах 7.1/7.8.1] as [Действ. точка СПО],
		  spo_base.[РД куратора ТТ]   as [РД ТТ СПО],
		  spo_base.[ФИО Куратора ТТ]  as [Куратор СПО],
		  spo_base.[ID Куратора ТТ]   as [Код куратора],
		  spo_base.[Наличие мотивации у агента],
		  spo_base.[Агент в чат боте] as [Агент в боте],
		  CASE WHEN reqs.num_of_reqs     is not null THEN reqs.num_of_reqs     ELSE 0 END as [К-во заявок],
		  CASE WHEN delivs.num_of_delivs is not null THEN delivs.num_of_delivs ELSE 0 END as [К-во выдач],
		  CASE WHEN acts.num_of_acts     is not null THEN acts.num_of_acts     ELSE 0 END as [К-во активаций],
		  ROW_NUMBER() OVER(PARTITION BY step1.[ID сотрудника] ORDER BY spo_base.[Статус агента DESS]) as r_n -- некоторые агенты мультиплицируются из-за повторов в СПО
	 INTO #FINBOX_AGENTS_W_DUPLICATES
     FROM #STEP_1 step1
LEFT JOIN #NUM_OF_AGENTS num_ags
       ON step1.[ID ТТ] = num_ags.[ID ТТ]
LEFT JOIN [TRANSPORT].[dbo].[SPO_BASE] spo_base
	   ON step1.[ID RBS агента] = CASE WHEN ISNUMERIC(spo_base.[ID RBS Агента]) = 1 THEN CAST(spo_base.[ID RBS Агента] AS numeric) ELSE null END
	  AND spo_base.[Статус агента DESS] != 'Доступ удален'
LEFT JOIN #REQUESTS reqs
       ON step1.[ID сотрудника] = reqs.OUT_USER_ID
LEFT JOIN #DELIVERIES delivs
       ON step1.[ID сотрудника] = delivs.OUT_USER_ID
LEFT JOIN #ACTIVATIONS acts
       ON step1.[ID сотрудника] = acts.OUT_USER_ID
--<
DELETE FROM [TRANSPORT].[dbo].[FINBOX_AGENTS]
INSERT INTO [TRANSPORT].[dbo].[FINBOX_AGENTS]
   SELECT [ID сотрудника],
          [ФИО сотрудника],
		  [Дата рождения],
		  [Место рождения по паспорту],
		  [Адрес по прописке],
		  [Паспорт],
		  [Код подразделения],
		  [Кем выдан],
		  [Дата выдачи паспорта],
		  [Номер телефона],
		  [ID ТТ],
		  [Тел., привязанный к «Халве»],
		  [Статус карты],
	      [ID карты],
		  [Кредитный договор],
		  [Наличие «Десятки»],
		  [Наличие ОМП],
		  [Последний вход в ОМП],
		  [Подключение Pay],
		  [Выполнение 5х10 в текущем ОП],
		  [Выполнение 5х10 в прошлом ОП],
		  [Агент в чат-боте],
		  [ID RBS агента],
		  [ИНН],
		  [Бренд],
		  [Категория],
		  [Адрес],
		  [ТТ],
		  [К-во агентов на ТТ],
		  [Логин СПО],
		  [Статус агента DESS],
		  [Действ. точка СПО],
		  [РД ТТ СПО],
		  [Куратор СПО],
		  [Код куратора],
		  [Наличие мотивации у агента],
		  [Агент в боте],
		  [К-во заявок],
		  [К-во выдач],
		  [К-во активаций]
     FROM #FINBOX_AGENTS_W_DUPLICATES
	WHERE r_n = 1
 ORDER BY CAST([ID сотрудника] AS numeric)
--<
   SELECT *
     FROM [TRANSPORT].[dbo].[FINBOX_AGENTS]
