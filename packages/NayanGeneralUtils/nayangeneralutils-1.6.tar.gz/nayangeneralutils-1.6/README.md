This is a personal python library including assorted general utilities i've standardised for my own reuse.

It currently includes the following modules:

fileHandling - Assorted functions to streamline reading and writing data with CSV, txt, and fig.png
	createFolder(directory, folderName)
	getData(filePath, fileName)
	saveCSV(filepath, filename, dataFrame)
	saveTxT(filepath, filename, text)
	saveFigure(directory, fileName, fig)

inputOutput - Assorted functions streamlining IO functions
	IObool(text, default=True, ynDict = {"y":True, "n":False})
	IOint(text, default=1)
	IOfloat(text, default=0)
	IOsaveTxT(text, fileName)
	IOsaveCSV(data, fileName)
	IOsaveFig(fig, fileName)

progress - Progress class; implements a basic timer object
	class progress
		__init__(self, startIt, totalIt)
		cls(self)
		increment(self, increment=1)
		display(self, title="", percentDisplay=True, rounding=2)
		timeElapsed(self)

plotting - includes a plotter class which streamlines matplotlib figure generation
	class plotter
		__init__(self, markerWidth=0.8, markerArea=12, gridColor='k', gridStyle='-',gridWidth=0.1, errCapsize=3, histWidth=0.5)
		display(self)
		saveFig(self, directory, fileName)
		
		axisLabels(self, xLabel="xData", yLabel="yData")
		axisTicks(self, xTicks, yTicks)
		gridline(self)
		legend(self, loc="upper right")
		
		scatter(self, xData, yData, marker = 'x', color='k', label="")
		scatterYer(self, xData, yData, yErr, color='k', label="")
		scatterXer(self, xData, yData, xErr, color='k', label="")
		scatterXYer(self, xData, yData, xErr, yErr, color='k', label="")
		histogram(self,xData, bins=10, color="r", label="")
		
EquationHandler - A module intended for symPy equation and expression handling
	sumExpressions(expressions)
	errorPropagationTerm(expression, variable)
	errorPropagate(expression, returnSymbols=False)

misc - Miscelaneous utilities
	strLinesConcatenate(strList, current="")

