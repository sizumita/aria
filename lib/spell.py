Const_trees={
	"generate":{
		"element":None
	},
	"change":{
		"element":{
			"sword":None,
			"spear":None,
			"bow":None,
			"wall":None,
			"wand":None
		},
		"feature":{
			"flame":None,
			"water":None,
			"earth":None,
			"light":None,
			"umbra":None
		}
	},
	"copy":"number",
	"execute":None
}
class Spell():
	def __init__(self):
		self.trees=[]
	def receive_command(self,command):
		commands=command.split(" ")
		try:
			self.loops(Const_trees[commands[0]],commands,1)
		except KeyError:
			self.typo()
	def loops(self,tree,commands,index):
		try:
			if isinstance(tree,str):
				if tree == "number":
					
					condition = (commands[index].isdecimal())
				if not condition:
					self.typo()
					return
			else:
				condition = (tree[commands[index]] == None)
			if condition and len(commands) == index+1:
				print("成功")
				command=" ".join(commands)
				#commandを色々して作って下さい
				return
			else:
				self.loops(tree[commands[index]],commands,index+1)
		except KeyError:
			self.typo()
		except IndexError:
			self.typo()
	def typo(self):
		#Typo処理
		print("Typo!")
if __name__=="__main__":
	s=Spell()
	s.receive_command(input())