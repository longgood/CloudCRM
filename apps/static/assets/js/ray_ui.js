//地圖載入(或可以再細分) https://ithelp.ithome.com.tw/articles/10223786

function disp_canvas(){
	testman=document.getElementById('tester');
	dataB.values[0]=55;
	Plotly.newPlot(testman, dataB, getLayout());
	
}
function randomize() {
  Plotly.animate('myDiv', {
    data: [{y: [Math.random(), Math.random(), Math.random()]}],
    traces: [0],
    layout: {}
  }, {
    transition: {
      duration: 500,
      easing: 'cubic-in-out'
    },
    frame: {
      duration: 500
    }
  })
}
function disp_trend(chartname,Value,XData=[],YAxisName='花費時間(秒)',XAxisName='場景')
{	
	var X=[];
	var N=0
	if (Value != null &&Value.length>0)
	{
		N=Value.length;
	}		
	var green=[100,166,77];
	var red=[190,57,72];
	if(XData.length==0){
		for (var i = 0; i <=N+1; i++){
			X.push(XAxisName+i)
		};	
	}else{
		//X=XData
		for (var i = 0; i <=N+1; i++){
			X.push(XData[i])
		};	
	}
	
	if (Value==null || N==0){
		N=1
		X=[""]
		Value=[0]
		YAxisName=""
		XAxisName="無執行資料"
	}
	PLOTMASTER=document.getElementById(chartname);

	var data = [
	  {
		x: X,
		y: Value,
		type: 'scatter',
		line: {
		width: 3
	}
	  }
		];


	Plotly.newPlot(PLOTMASTER, data);
	
}
function disp_chart(chartname,ValueA=[2,4,8,16,10,8],ValueAName='髖關節',ValueB=[],ValueBName='',YAxisName='角度王(。)',XAxisName='時間序列',)
{
	var X=[];
	var N=ValueA.length;
	var green=[100,166,77];
	var red=[190,57,72];
	for (var i = 0; i <=N+1; i++){
		X.push(i)
	};
	
	PLOTMASTER=document.getElementById(chartname);
	//資料A的設定
	var traceA = {
	  x: X,
	  y: ValueA,
	  type:'scatter',
	  name: ValueAName,
	  line: {
		color: 'rgb(94, 162, 182)',
		width: 3
	  }
	};
	//資料B的設定
	
	var traceB = {
	  x: X,
	  y: ValueB,
	  type: 'scatter',
	 // mode: 'lines',
	  name: ValueBName,
	  line: {
		color: 'rgb(239, 193, 52)',
		width: 3
	  }
	};
	var data = [traceA, traceB];
	var layout = {
		 
		  xaxis: {
			  title:XAxisName,
			  tickfont: {
			  size: 14,
			  color: 'rgb(107, 107, 107)'
			}},
			yaxis: {
			  title:YAxisName,
			  tickfont: {
			  size: 14,
			  color: 'rgb(107, 107, 107)'
			}},
			legend: {
			x: 1,
			y: 0.0}
			
	};


	Plotly.newPlot(PLOTMASTER, data,layout);
	
}
function disp_bar(chartname,Value,XData=[],YAxisName='花費時間(秒)',XAxisName='場景')
{	
	var X=[];
	var N=0
	if (Value != null &&Value.length>0)
	{
		N=Value.length;
	}		
	var green=[100,166,77];
	var red=[190,57,72];
	if(XData.length==0){
		for (var i = 0; i <=N+1; i++){
			X.push(XAxisName+i)
		};	
	}else{
		X=XData
		
	}
	
	if (Value==null || N==0){
		N=1
		X=[""]
		Value=[0]
		YAxisName=""
		XAxisName="無執行資料"
	}
	PLOTMASTER=document.getElementById(chartname);

	var data = [
	  {
		x: X,
		y: Value,
		type: 'bar'
	  }
		];
	var layout = {
		 
		  xaxis: {
			  title:XAxisName,
			  tickangle: -45,
			  tickfont: {
			  size: 14,
			  color: 'rgb(107, 107, 107)'
			}},
			yaxis: {
			  title:YAxisName,
			  tickfont: {
			  size: 14,
			  color: 'rgb(107, 107, 107)'
			}},
			legend: {
			x: 1,
			y: 0.0}
			
	};


	Plotly.newPlot(PLOTMASTER, data,layout);
	
}
function disp_pie(chartname,Value=[2,4,8,16,10,8],ValueName=['髖關節','居家活動'],Title='',)
{
	PLOTMASTER=document.getElementById(chartname);
	var data = [{
		values: Value,
		labels: ValueName,
		type: 'pie',
		hole: .4
	}];

	var layout = {
    title: Title
	};

	var config = {
	showEditInChartStudio: false,
	plotlyServerURL: "https://chart-studio.plotly.com"
	};

	Plotly.newPlot(PLOTMASTER, data, layout);
}
function disp_radar(chartname,Value=[12,4,8,16,10,8],Theta=["財務","交通","居家","儲物","煮飯"],Title='',)
{
	PLOTMASTER=document.getElementById(chartname);

	data = [{
	  type: 'scatterpolar',
	  r:Value,
	  theta: Theta,
	  fill: 'toself'
	}]

	layout = {
	  polar: {
		radialaxis: {
		  visible: true,
		  range: [0, Math.max(...Value)]
		}
	  },
	  showlegend: false
	}
	//Plotly.newPlot(PLOTMASTER, data, layout);
	Plotly.newPlot(PLOTMASTER, data,layout);
}
function disp_radar_dual(chartname,ValueA=[12,4,8,16,10,8],ValueB=[2,15,3,3,4,18],Theta=["財務","交通","居家","儲物","煮飯"],Title='前後兩週比較',SubTitleA="前週",SubTitleB="現況")
{
	PLOTMASTER=document.getElementById(chartname);

	data = [
		 {
	  type: 'scatterpolar',
	  r: ValueA,
	  theta: Theta,
	  fill: 'toself',
	  name: SubTitleA
	  },
	  {
	  type: 'scatterpolar',
	  r: ValueB,
	  theta: Theta,
	  fill: 'toself',
	  name: SubTitleB
	  }
	]
	layout = {
	  title:Title,
	  polar: {
		radialaxis: {
		  visible: true,
		  range: [0,Math.max( Math.max(...ValueA),Math.max(...ValueB))]
		}
	  },
	  showlegend: true
	}
	Plotly.newPlot(PLOTMASTER, data,layout);
}

