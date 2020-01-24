import heapq
import json
import math
class TreeNode():
    def __init__(self,freq,char):
        self.freq = freq
        self.char=char
        self.right=None
        self.left=None

    def __gt__(self, other):
        if(self.freq >other.freq):
            return 1
        else:
            return 0
def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ''.join(format(ord(letter), 'b') for letter in str)
    return binary


def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)  
    return d
def create_frequency_table(text):
    freq={}
    for char in text:
        if(not char in freq):
            freq[char] = 1
        else:
            freq[char] +=1
    return freq


def create_tree(freq):
    #build heap
    heap=[]
    for key in freq:
        node=TreeNode(freq[key], key)
        heapq.heappush(heap,node) #push in heap
    
    while(len(heap)>1):
        #pop nodes with least frequency, and merge them into one node
        #add the children and push into the heap
        first_node=heapq.heappop(heap)
        second_node=heapq.heappop(heap)

        merged_node = TreeNode(first_node.freq+second_node.freq,None)
        merged_node.left=first_node
        merged_node.right=second_node

        heapq.heappush(heap,merged_node)

    return heap

def encode_letters(root_node,code,codes_dict,reverse_lookup_dict):
    #codes_dict: has the bin codes of each character
    #root_node is the last node in the heap (in the first itteration)
    if(root_node.char==None):
        #if not a letter: call on left and right child with appended 0 and 1
        #in the code respectively
        encode_letters(root_node.left,code+'0',codes_dict,reverse_lookup_dict)
        encode_letters(root_node.right,code+'1',codes_dict,reverse_lookup_dict)
    else:
        #if a letter is reached: append the dict with the letter and its code
        codes_dict[root_node.char]=code
        reverse_lookup_dict[code]=root_node.char #for decompression
def get_byte_array(padded_encoded_text):
		if(len(padded_encoded_text) % 8 != 0):
			print("Encoded text not padded properly")
			exit(0)

		b = bytearray()
		for i in range(0, len(padded_encoded_text), 8): #take each 8 bits(byte)
			byte = padded_encoded_text[i:i+8]
			b.append(int(byte, 2))
		return b
def pad_encoded_text(encoded_text):
		extra_padding = 8 - len(encoded_text) % 8
		for i in range(extra_padding):
			encoded_text += "0"

		padded_info = "{0:08b}".format(extra_padding)
		encoded_text = padded_info + encoded_text
		return encoded_text
def compress_file(path):
    try:
        file = open(path, 'r',encoding='utf8')
    except :
        print("no such file or directory")
    
    text = file.read()
    freq=create_frequency_table(text)

    #get number of chars in the text file
    #put each char and probability in dict 
    number_of_chars=len(text)
    probabilitites_dict={}
    symbols_keys=freq.keys()
    for key in symbols_keys:
        probabilitites_dict[key]=freq[key]/number_of_chars

    heap = create_tree(freq)
    root_node=heapq.heappop(heap)
    code=""
    codes_dict={}
    reverse_lookup_dict={}
    encode_letters(root_node,code,codes_dict,reverse_lookup_dict)

    #get length of bits of each symbol
    symbols_lengths_dict = {}
    for key in codes_dict.keys():
        symbols_lengths_dict[key] = len(codes_dict[key])

    #compute <L>
    avg_len=0
    for key in symbols_keys:
        avg_len+=symbols_lengths_dict[key]*probabilitites_dict[key]

    #compute H entropy
    H=0
    for key in symbols_keys:
        H+=probabilitites_dict[key]*math.log(1/probabilitites_dict[key],2)
    
    #compute effeciency n
    effeciency = H/avg_len
    print("Average Length = " , avg_len , "\n Entropy (H) = " , H , "\n Effeciency = " , effeciency ,'\n')



    #get the coded text
    coded_text=""
    for char in text:
        coded_text+=codes_dict[char]
    open('dictionary.txt', 'wb').close()
    
    with open("encoded_text.bin", 'wb') as file:
        dict_file=open('dictionary.txt','r+')
        #Save the dictionary in binary file format
        #binary_dictionary=dict_to_binary(reverse_lookup_dict)
        #padded = pad_encoded_text(binary_dictionary)
        #bArray=get_byte_array(padded)
        #file.write(bytes(bArray))
        dict_file.write(json.dumps(reverse_lookup_dict))

        #size = open('size.txt','w')
        #size.write(str(len(binary_dictionary)))

        #Save Text in Binary format
        padded = pad_encoded_text(coded_text)
        bArray=get_byte_array(padded)
        file.write(bytes(bArray))
    return coded_text

def remove_padding(padded_encoded_text):
    padded_info = padded_encoded_text[:8] #first byte is the padding info
    extra_padding = int(padded_info, 2) #change the number to binary
    padded_encoded_text = padded_encoded_text[8:] #cut the added padding info from the text
    encoded_text = padded_encoded_text[:-1*extra_padding]#cut the added padding
    return encoded_text

    
def decompress_file(path):
    try:
        file = open(path, 'rb').close()
        file = open(path, 'rb')
        dictionary = open('dictionary.txt','r+')
        #size =open('size.txt','r',encoding="utf8")
    except :
        print("no such file or directory")
    #dict_size=int(size.read())
    #text = file.read(dict_size)
    #from bitstring import BitStream, BitArray
    #bits=BitArray(bytes=text)
    #bits = bits.bin[:dict_size]
    #bits=bits[0:7]+' '+bits[7:]
    #bits=bits[:len(bits)-7]+' '+bits[len(bits)-7:]
    #reverse_lookup_dict=binary_to_dict(bits)
    dictionary_text = dictionary.read()
    reverse_lookup_dict=json.loads(dictionary_text) #dict to lookup the bin code for the char
    text = file.read()
    from bitstring import BitArray
    text=BitArray(bytes=text).bin

    text=remove_padding(text)
    decoded_text=""
    decoded_letter=""
    #a=text.split('_')
    for bin_num in text:
        decoded_letter+=bin_num
        if(decoded_letter in reverse_lookup_dict):
            decoded_text+=reverse_lookup_dict[decoded_letter]
            decoded_letter=''

    open('decoded_text.txt', 'w').close()
    file = open('decoded_text.txt','r+')
    file.write(decoded_text)
    return 

import os
import sys

path = sys.argv[2]
comp_decomp=sys.argv[1]
if os.path.exists(path):
    if(comp_decomp=='0'):
        compress_file(path)
    else :
        decompress_file(path)
else:
    print("no such file or directory")



#compress_file("text.txt")
#decompress_file("encoded_text.bin")
#print("")

