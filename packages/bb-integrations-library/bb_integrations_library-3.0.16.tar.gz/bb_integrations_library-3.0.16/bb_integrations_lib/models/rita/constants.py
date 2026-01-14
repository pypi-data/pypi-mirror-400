parent_keys = [{'field': 'id', 'hide': True},
               {'field': 'source_id', 'filter': True, 'editable': True, 'headerName': 'Source Id'},
               {'field': 'gravitate_id', 'filter': True, 'editable': True, 'headerName': 'Gravitate Id'},
               {'field': 'updated_by', 'filter': True, 'headerName': 'Updated By'},
               {'field': 'updated_on', 'filter': True, 'headerName': 'Updated On', 'type': 'datetime'},
               {'field': 'type', 'filter': True, 'headerName': 'Type'},
               {'field': 'source_system', 'filter': True, 'headerName': 'Source System'},

               ]
children_keys = [{'field': 'id', 'hide': True},
                 {'field': 'parent_id', 'hide': True},
                 {'field': 'source_id', 'filter': True, 'editable': True, 'headerName': 'Source Id'},
                 {'field': 'gravitate_id', 'filter': True, 'editable': True, 'headerName': 'Gravitate Id'},
                 {'field': 'parent_source_id', 'filter': True, 'headerName': 'Parent Source ID'},
                 {'field': 'parent_gravitate_id', 'filter': True, 'headerName': 'Parent Gravitate Id'},
                 {'field': 'parent_type', 'filter': True, 'headerName': 'Parent Type'},
                 {'field': 'updated_by', 'filter': True, 'headerName': 'Updated By'},
                 {'field': 'updated_on', 'filter': True, 'headerName': 'Updated On'},
                 ]