import json
import jsonlines
import pickle
from classes.campaign import Campaign
from classes.input_processor import InputProcessor
from keys import Keys
class BigCampaign():
    def __init__(self, path:str = "", campaign_id:str = ""):
        self.data = list()
        self.id = campaign_id
        self.input_processor = InputProcessor()
        
        # Handle JSON files (existing functionality)
        if path.endswith(".json"):
            with open(path, "r") as f:
                data = json.load(f)
                if len(data) == 0:
                    return
                for d in data:
                    id_ = d["id"]
                    text = d["text"]
                    campaign = Campaign(text=text, id=id_, image_path="")
                    self.data.append(campaign)
            self.phrases_gathering()
            
        # Handle URLs, HTML, PDF, and text files using universal processor
        else:
            print(f"Processing input: {path}")
            print(f"Input type: {self.input_processor.get_input_type(path)}")
            
            # Extract text content using universal processor
            text = self.input_processor.process_input(path)
            
            if text and text.strip():
                print(f"Extracted {len(text)} characters of content")
                
                if Keys.ENABLE_BIG_CAMPAIGN:
                    # Split by sentences or paragraphs for better processing
                    texts = self._smart_text_split(text)
                    for idx, text_chunk in enumerate(texts):
                        if text_chunk.strip():
                            campaign = Campaign(text=text_chunk.strip(), id=idx, image_path="")
                            self.data.append(campaign)
                else:
                    campaign = Campaign(text=text, id=0, image_path="")
                    self.data.append(campaign)
                    
                self.phrases_gathering()
            else:
                print(f"No content extracted from {path}")

    def _smart_text_split(self, text: str) -> list:
        """
        Smart text splitting that preserves context while breaking into manageable chunks
        """
        import re
        
        # First try to split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # If paragraphs are too long, split by sentences
        final_chunks = []
        for para in paragraphs:
            if len(para) > 1000:  # If paragraph is too long
                # Split by sentences using periods, exclamation marks, question marks
                sentences = re.split(r'(?<=[.!?])\s+', para)
                
                # Group sentences into chunks of reasonable size
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk + sentence) < 800:  # Keep chunks under 800 chars
                        current_chunk += sentence + " "
                    else:
                        if current_chunk.strip():
                            final_chunks.append(current_chunk.strip())
                        current_chunk = sentence + " "
                
                if current_chunk.strip():
                    final_chunks.append(current_chunk.strip())
            else:
                final_chunks.append(para)
        
        # If we still don't have good splits, fall back to simple line splitting
        if not final_chunks or len(final_chunks) == 1:
            final_chunks = [line.strip() for line in text.split('\n') if line.strip()]
        
        return final_chunks if final_chunks else [text]

    def to_jsonl(self, path:str):
        new_data = []
        for d in self.data:
                dict_obj = d.to_dict()
                new_data.append(dict_obj)
        with jsonlines.open(path, mode="w") as writer:
            writer.write_all(new_data)
    def to_pickle(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self, f)
    def from_jsonl(self, path:str, campaign_id:str = ""):
        with jsonlines.open(path, "r") as reader:
            for line in reader.iter():
                json_object = line
                campaign = Campaign()
                campaign.from_json_object(json_object)
                self.data.append(campaign)
        self.phrases_gathering()
        self.id = campaign_id
    def mapper_gathering(self):
        self.mapper = dict()
        start_id = 0
        start_sent_id = 0
        for campaign in self.data:
            
            for k,v in campaign.mapper.items():
                new_k = start_id + k # update the id
                self.mapper[new_k] = []
                for vv in v:
                    new_vv = vv.copy()
                    new_vv["min_id"] += start_id
                    order_ids = [0]*len(vv["order_ids"])
                    sent_indexes = [0]*len(vv["sent_indexes"])
                    combined_ids = [0]*len(vv["combine_ids"])
                    for i in range(len(vv["order_ids"])):
                        order_ids[i] = vv["order_ids"][i] + start_id
                        sent_indexes[i] = vv["sent_indexes"][i] + start_sent_id
                    for i in range(len(vv["combine_ids"])):
                        combined_ids[i] = vv["combine_ids"][i] + start_sent_id * 1000
                    new_vv["order_ids"] = order_ids
                    new_vv["sent_indexes"] = sent_indexes
                    new_vv["combine_ids"] = combined_ids
                    self.mapper[new_k].append(new_vv)
            start_id += len(campaign.graph_nodes)
            start_sent_id += len(campaign.sentences)
            print()
    def tech_mapper_gathering(self):
        self.tech_alignment = dict()
        start_id = 0
        start_sent_id = 0
        for campaign in self.data:
            for k,v in campaign.tech_alignment.items():
                new_k = start_id + k
                self.tech_alignment[new_k] = []
                for vv in v:
                    new_vv = vv.copy()
                    new_vv["min_id"] += start_id
                    order_ids = [0]*len(vv["order_ids"])
                    sent_indexes = [0]*len(vv["sent_indexes"])
                    for i in range(len(vv["order_ids"])):
                        order_ids[i] = vv["order_ids"][i] + start_id
                        sent_indexes[i] = vv["sent_indexes"][i] + start_sent_id
                    new_vv["order_ids"] = order_ids
                    new_vv["sent_indexes"] = sent_indexes
                    self.tech_alignment[new_k].append(new_vv)
            start_id += len(campaign.graph_nodes)
            start_sent_id += len(campaign.sentences)
    def phrases_gathering(self):
        self.phrases = []
        for campaign in self.data:
            if hasattr(campaign, "phrases"):
                self.phrases.extend(campaign.phrases)
        self.phrases = list(set(self.phrases))