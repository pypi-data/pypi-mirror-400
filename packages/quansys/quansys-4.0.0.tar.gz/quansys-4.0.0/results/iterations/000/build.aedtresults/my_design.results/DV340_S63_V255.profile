$begin 'Profile'
	$begin 'ProfileGroup'
		MajorVer=2024
		MinorVer=2
		Name='Solution Process'
		$begin 'StartInfo'
			I(1, 'Start Time', '01/05/2026 13:28:21')
			I(1, 'Host', 'CMD-SRSTUDENT3')
			I(1, 'Processor', '16')
			I(1, 'OS', 'NT 10.0')
			I(1, 'Product', 'HFSS Version 2024.2.0')
		$end 'StartInfo'
		$begin 'TotalInfo'
			I(1, 'Elapsed Time', '00:00:26')
			I(1, 'ComEngine Memory', '145 M')
		$end 'TotalInfo'
		GroupOptions=8
		TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
		ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 1, \'Executing From\', \'C:\\\\Program Files\\\\AnsysEM\\\\v242\\\\Win64\\\\HFSSCOMENGINE.exe\')', false, true)
		$begin 'ProfileGroup'
			MajorVer=2024
			MinorVer=2
			Name='HPC'
			$begin 'StartInfo'
				I(1, 'Type', 'Auto')
				I(1, 'MPI Vendor', 'Intel')
				I(1, 'MPI Version', '2021')
			$end 'StartInfo'
			$begin 'TotalInfo'
				I(0, ' ')
			$end 'TotalInfo'
			GroupOptions=0
			TaskDataOptions(Memory=8)
			ProfileItem('Machine', 0, 0, 0, 0, 0, 'I(5, 1, \'Name\', \'cmd-srstudent3\', 1, \'Memory\', \'31.9 GB\', 3, \'RAM Limit\', 90, \'%f%%\', 2, \'Cores\', 4, false, 1, \'Free Disk Space\', \'57 GB\')', false, true)
		$end 'ProfileGroup'
		ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 1, \'Allow off core\', \'True\')', false, true)
		ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 1, \'Solution Basis Order\', \'Mixed\')', false, true)
		ProfileItem('Design Validation', 0, 0, 0, 0, 0, 'I(1, 0, \'Elapsed time : 00:00:00 , HFSS ComEngine Memory : 143 M\')', false, true)
		ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 0, \'Perform full validations with standard port validations\')', false, true)
		ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 0, \'\')', false, true)
		$begin 'ProfileGroup'
			MajorVer=2024
			MinorVer=2
			Name='Initial Meshing'
			$begin 'StartInfo'
				I(1, 'Time', '01/05/2026 13:28:21')
			$end 'StartInfo'
			$begin 'TotalInfo'
				I(1, 'Elapsed Time', '00:00:08')
			$end 'TotalInfo'
			GroupOptions=4
			TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
			ProfileItem('Stitch', 1, 0, 0, 0, 72364, 'I(1, 2, \'Triangles\', 994, false)', true, true)
			ProfileItem('Mesh', 0, 0, 0, 0, 76840, 'I(2, 1, \'Type\', \'Classic\', 2, \'Tetrahedra\', 3078, false)', true, true)
			ProfileItem('Post', 1, 0, 0, 0, 80876, 'I(2, 2, \'Tetrahedra\', 3430, false, 2, \'Cores\', 1, false)', true, true)
			ProfileItem('Manual Refine', 5, 0, 5, 0, 117832, 'I(3, 2, \'Tetrahedra\', 36211, false, 2, \'Cores\', 1, false, 0, \'chip_base_mesh, readout_mesh\')', true, true)
			ProfileItem('Lambda Refine', 0, 0, 0, 0, 88292, 'I(2, 2, \'Tetrahedra\', 36984, false, 2, \'Cores\', 1, false)', true, true)
		$end 'ProfileGroup'
		$begin 'ProfileGroup'
			MajorVer=2024
			MinorVer=2
			Name='Adaptive Meshing'
			$begin 'StartInfo'
				I(1, 'Time', '01/05/2026 13:28:30')
			$end 'StartInfo'
			$begin 'TotalInfo'
				I(1, 'Elapsed Time', '00:00:17')
			$end 'TotalInfo'
			GroupOptions=4
			TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
			$begin 'ProfileGroup'
				MajorVer=2024
				MinorVer=2
				Name='Adaptive Pass 1'
				$begin 'StartInfo'
					I(0, 'Eigenmode Solution')
				$end 'StartInfo'
				$begin 'TotalInfo'
					I(0, ' ')
				$end 'TotalInfo'
				GroupOptions=0
				TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
				ProfileItem('Simulation Setup', 0, 0, 0, 0, 288088, 'I(1, 1, \'Disk\', \'14.4 KB\')', true, true)
				ProfileItem('Matrix Assembly', 0, 0, 1, 0, 303036, 'I(2, 2, \'Tetrahedra\', 36984, false, 1, \'Disk\', \'0 Bytes\')', true, true)
				ProfileItem('Matrix Solve', 0, 0, 1, 0, 399240, 'I(6, 1, \'Type\', \'DRS\', 2, \'Cores\', 4, false, 2, \'Matrix size\', 47315, false, 3, \'Matrix bandwidth\', 9.99049, \'%5.1f\', 2, \'Eigen iterations\', 8, false, 1, \'Disk\', \'739 KB\')', true, true)
				ProfileItem('Field Recovery', 0, 0, 1, 0, 422724, 'I(3, 2, \'Computed eigenmodes\', 1, false, 3, \'Average order\', 0.0830427, \'%f\', 1, \'Disk\', \'13.4 MB\')', true, true)
			$end 'ProfileGroup'
			ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 0, \'\')', false, true)
			$begin 'ProfileGroup'
				MajorVer=2024
				MinorVer=2
				Name='Adaptive Pass 2'
				$begin 'StartInfo'
					I(0, 'Eigenmode Solution')
				$end 'StartInfo'
				$begin 'TotalInfo'
					I(0, ' ')
				$end 'TotalInfo'
				GroupOptions=0
				TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
				ProfileItem('Adaptive Refine', 2, 0, 2, 0, 106520, 'I(2, 2, \'Tetrahedra\', 48081, false, 2, \'Cores\', 1, false)', true, true)
				ProfileItem('Simulation Setup', 0, 0, 0, 0, 313836, 'I(1, 1, \'Disk\', \'22.7 KB\')', true, true)
				ProfileItem('Matrix Assembly', 1, 0, 2, 0, 366324, 'I(2, 2, \'Tetrahedra\', 48081, false, 1, \'Disk\', \'0 Bytes\')', true, true)
				ProfileItem('Matrix Solve', 1, 0, 4, 0, 594384, 'I(6, 1, \'Type\', \'DRS\', 2, \'Cores\', 4, false, 2, \'Matrix size\', 97293, false, 3, \'Matrix bandwidth\', 14.7492, \'%5.1f\', 2, \'Eigen iterations\', 8, false, 1, \'Disk\', \'781 KB\')', true, true)
				ProfileItem('Field Recovery', 0, 0, 1, 0, 606652, 'I(3, 2, \'Computed eigenmodes\', 1, false, 3, \'Average order\', 0.35408, \'%f\', 1, \'Disk\', \'8.95 MB\')', true, true)
				ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 3, \'Max Delta Freq. %\', 1.92257, \'%.5f\')', false, true)
			$end 'ProfileGroup'
			ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 0, \'\')', false, true)
			$begin 'ProfileGroup'
				MajorVer=2024
				MinorVer=2
				Name='Adaptive Pass 3'
				$begin 'StartInfo'
					I(0, 'Eigenmode Solution')
				$end 'StartInfo'
				$begin 'TotalInfo'
					I(0, ' ')
				$end 'TotalInfo'
				GroupOptions=0
				TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
				ProfileItem('Adaptive Refine', 1, 0, 1, 0, 103844, 'I(2, 2, \'Tetrahedra\', 54677, false, 2, \'Cores\', 1, false)', true, true)
				ProfileItem('Simulation Setup', 0, 0, 0, 0, 326576, 'I(1, 1, \'Disk\', \'22.7 KB\')', true, true)
				ProfileItem('Matrix Assembly', 1, 0, 2, 0, 417884, 'I(2, 2, \'Tetrahedra\', 54677, false, 1, \'Disk\', \'0 Bytes\')', true, true)
				ProfileItem('Matrix Solve', 2, 0, 7, 0, 796132, 'I(6, 1, \'Type\', \'DRS\', 2, \'Cores\', 4, false, 2, \'Matrix size\', 146964, false, 3, \'Matrix bandwidth\', 16.9684, \'%5.1f\', 2, \'Eigen iterations\', 8, false, 1, \'Disk\', \'776 KB\')', true, true)
				ProfileItem('Field Recovery', 0, 0, 2, 0, 796132, 'I(3, 2, \'Computed eigenmodes\', 1, false, 3, \'Average order\', 0.534306, \'%f\', 1, \'Disk\', \'6.58 MB\')', true, true)
				ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 3, \'Max Delta Freq. %\', 0.7097, \'%.5f\')', false, true)
			$end 'ProfileGroup'
			ProfileFootnote('I(1, 0, \'Adaptive Passes did not converge\')', 1)
		$end 'ProfileGroup'
		ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 0, \'\')', false, true)
		$begin 'ProfileGroup'
			MajorVer=2024
			MinorVer=2
			Name='Simulation Summary'
			$begin 'StartInfo'
			$end 'StartInfo'
			$begin 'TotalInfo'
				I(0, ' ')
			$end 'TotalInfo'
			GroupOptions=0
			TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
			ProfileItem('Design Validation', 0, 0, 0, 0, 0, 'I(2, 1, \'Elapsed Time\', \'00:00:00\', 1, \'Total Memory\', \'143 MB\')', false, true)
			ProfileItem('Initial Meshing', 0, 0, 0, 0, 0, 'I(2, 1, \'Elapsed Time\', \'00:00:08\', 1, \'Total Memory\', \'115 MB\')', false, true)
			ProfileItem('Adaptive Meshing', 0, 0, 0, 0, 0, 'I(3, 1, \'Elapsed Time\', \'00:00:17\', 1, \'Total Memory\', \'1.74 GB\', 2, \'Total number of cores\', 4, false)', false, true)
			ProfileFootnote('I(3, 2, \'Max solved tets\', 54677, false, 2, \'Max matrix size\', 146964, false, 1, \'Matrix bandwidth\', \'17.0\')', 0)
		$end 'ProfileGroup'
		ProfileFootnote('I(2, 1, \'Stop Time\', \'01/05/2026 13:28:48\', 1, \'Status\', \'Normal Completion\')', 0)
	$end 'ProfileGroup'
$end 'Profile'
