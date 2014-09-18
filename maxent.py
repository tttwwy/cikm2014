import maxent.pymaxent as pymaxent
import maxent.cmaxent as cmaxent

m = cmaxent.MaxentModel()
m.begin_add_event()
with open("test.data","r") as f:
	for line in f:
		line = line.strip().split()
		context = line[1:]
		label = line[0]
		m.add_event(context,label)

m.end_add_event()
m.train(150, 'lbfgs', 4, 1E-05)
print m.eval(['Rainy'], 'Outdoor')
print m.eval(['Rainy'], 'Indoor')
# print m
