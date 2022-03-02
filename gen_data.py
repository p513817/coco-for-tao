import json, os, time, argparse, shutil, random, cv2
from tqdm import tqdm

def yolo_mapping(key, val):
    ret = '{}target_class_mapping {} \n{}key: "{}"\n{}value: "{}"\n {}'.format(
        '  ', '{', '    ', key, '    ', val, '}\n')
    return ret

def parse_data(json_path, tao_yolo_map=True):

    with open(json_path, 'r') as jsonfile:
        json_data = json.load(jsonfile)

    image_data = json_data['images']
    annot_data = json_data['annotations']
    categ_data = json_data['categories']
    new_category_dict, new_image_dict, new_annot_dict = {}, {}, {}

    for categ in categ_data:
        new_category_dict[categ['id']]={
            "supercategory":f"{categ['supercategory']}",
            "name":f"{categ['name']}"
        }

    for data in image_data:
        new_image_dict[data['id']]={
            "file_name": data['file_name'],
            "width": data['width'],
            "height": data['height']
        }

    for data in annot_data:
        new_annot_dict[ data['image_id'] ]={ 
            "bbox":data['bbox'],
            "category_id": data['category_id'],
            "id": data['id']    
        }

    # write simplify json
    key = 'train' if 'train' in json_path else 'val'
    folder = './simplify_json'
    if not os.path.exists(folder): os.makedirs(folder)
    with open(f'{folder}/{key}_image.json', 'w') as j:
        json.dump(new_image_dict, j)
    with open(f'{folder}/{key}_annot.json', 'w') as j:
        json.dump(new_annot_dict, j)
    with open(f'{folder}/{key}_categ.json', 'w') as j:
        json.dump(new_category_dict, j)

    if tao_yolo_map:
        with open(f'{folder}/yolo_mapping_table.txt', 'w') as f:
            for categ in categ_data:
                f.write( yolo_mapping(categ['supercategory'], categ['name']) )

    return new_image_dict, new_annot_dict, new_category_dict

def min_max(val, vmin, vmax):
    if val >= vmax:
        val = vmax
    if val <= vmin:
        val = vmin
    return val

def bbox_voc2norm(x, y, w, h, width, height):
    """
    convert bounding box's format from voc to kitti ( for TAO ):
    
        YOLO: center_x, center_y, width, height
        VOC: top_left_x, top_left_y, width, height
        Normal: top_left_x, top_left_y, bottom_right_x, bottom_right_y
    """

    x,y,w,h=map(float, (x,y,w,h))
    
    x1, y1 = (x), (y)
    x2, y2 = (x+w), (y+h)
    
    x1, x2 = [ min_max(val, 0, width) for val in [x1, x2] ]
    y1, y2 = [ min_max(val, 0, height) for val in [y1, y2] ]
    
    return x1, y1, x2, y2

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='path to mapping table')
    args = parser.parse_args()
    
    with open( args.config ) as jsonfile:
        config = json.load(jsonfile)

    target_list = [ 'train', 'val']

    for target in target_list:

        trg_config = config[target]

        if not trg_config['enable']: continue
        
        json_file, src_image_dir, dst_image_dir, dst_label_dir = trg_config['json_file'], trg_config['src_image_dir'], trg_config['dst_image_dir'], trg_config['dst_label_dir']

        image_info, annot_info, category_info = parse_data(json_file)

        # create
        if not os.path.exists(src_image_dir):
            raise Exception('could find image, please check the directory of image')
        [ os.makedirs(trg_dir) for trg_dir in [dst_image_dir, dst_label_dir] if not os.path.exists(trg_dir) ]
         
        image_id = list( (*image_info,) )
        num_images = len(image_id)
        ratio = config['reduce_ratio']
        limit = int(num_images*ratio)
        print(f'[{target}] Copy {limit} images to {dst_image_dir} ( ratio {ratio:03}% )')
        
        # limit = 1
        random.shuffle(image_id)
        for file_id in tqdm(image_id[:limit]):
            # ---------------------------------------------------------------------------------------------------------------
            # parse Information
            
            image = image_info[file_id]
            file_name = image["file_name"]
            
            src_image_path = os.path.join(src_image_dir, file_name)
            dst_image_path = os.path.join(dst_image_dir, file_name)
            label_path = os.path.join(dst_label_dir, "{}.txt".format(os.path.splitext(file_name)[0]))
            
            # update anotation information
            get_annotation = False

            if (file_id in annot_info.keys()): 
                get_annotation = True
                annot = annot_info[file_id]
                x, y, w, h = annot['bbox']
                x1, y1, x2, y2 = bbox_voc2norm(x, y, w, h, image["width"], image["height"])
                categ_id = annot['category_id']
                categ_name = category_info[categ_id]['name']
                
            # ---------------------------------------------------------------------------------------------------------------
            # copy image file
            shutil.copy(src_image_path, dst_image_path)

            # ---------------------------------------------------------------------------------------------------------------
            # create label file
            with open(label_path, "a") as label:
                label.write('"{category_name}" 0.00 0 0.00 {x1} {y1} {x2} {y2} 0.00 0.00 0.00 0.00 0.00 0.00 0.00'.format(
                    category_name=categ_name,
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2
                ) if get_annotation else " " )

    # spit test data from train
    if config['test']['enable']:

        src_image_dir, src_label_dir = config['train']['dst_image_dir'], config['train']['dst_label_dir']     # get source directory
                            
        split_ratio = float(config['test']['split_ratio_from_train'])                                                  # get destination directory
        dst_image_dir, dst_label_dir = config['test']['dst_image_dir'], config['test']['dst_label_dir']
        [ os.makedirs(dst_dir) for dst_dir in [dst_image_dir, dst_label_dir] if not os.path.exists(dst_dir) ]

        training_data = os.listdir(src_image_dir)
        num_testing_data = int(len(training_data)*split_ratio)
        print('Got number of training data: {}'.format(len(training_data)))
        print('The number of testing data:{} (split rate is {}％) '.format(num_testing_data, split_ratio*100) )
        random.shuffle(training_data)

        for file in tqdm(training_data[:num_testing_data]):
            
            file_name = os.path.splitext(file)[0]
            src_file_path = os.path.join(src_image_dir, file)
            src_label_path = os.path.join(src_label_dir, f"{file_name}.txt")

            dst_file_path = os.path.join(dst_image_dir, file)
            dst_label_path = os.path.join(dst_label_dir, f"{file_name}.txt")
            # copy file
            shutil.move(src_file_path, dst_file_path)
            shutil.move(src_label_path, dst_label_path)
    
    print('-'*30)
    if config['train']['enable']:
        print('Got {:7} Training data,\t labels: {:7}'.format( len(os.listdir(config['train']['dst_image_dir'])),
                                                        len(os.listdir(config['train']['dst_label_dir'])) ))
    if config['test']['enable']:
        print('Got {:7} Testing data, \t labels: {:7}'.format(  len(os.listdir(config['test']['dst_image_dir'])),
                                                        len(os.listdir(config['test']['dst_label_dir'])) ))
    if config['val']['enable']:
        print('Got {:7} Validate data,\t labels: {:7} '.format(  len(os.listdir(config['val']['dst_image_dir'])),
                                                            len(os.listdir(config['val']['dst_label_dir'])) ))
