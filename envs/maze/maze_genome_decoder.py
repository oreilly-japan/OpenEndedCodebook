import os
import numpy as np
import matplotlib.pyplot as plt

from maze_environment_numpy  import MazeEnvironment

class MazeGenomeDecoder:

    def __init__(self, config, maze_kwargs={}, agent_kwargs={}):
        self.region_max_size = (config.region_max_width, config.region_max_height)
        self.region_min_size = (config.region_min_width, config.region_min_height)
        self.maze_scaler = config.maze_scaler
        self.max_timesteps = config.max_timesteps
        self.maze_kwargs = maze_kwargs
        self.agent_kwargs = agent_kwargs

    # main decode function (maze genome -> wall list [(x1, y1, x2, y2)])
    def decode(self, genome, config, save=None, return_env=True):
        maze_size = genome.maze_size
        wall_genes = genome.wall_genes
        path_genes = genome.path_genes

        pathway_map = np.zeros((maze_size[1], maze_size[0]), dtype=int)
        horizontal_wall_map = np.zeros((maze_size[1]+1, maze_size[0]), dtype=bool)
        vertical_wall_map = np.zeros((maze_size[1], maze_size[0]+1), dtype=bool)

        path_length = self.track_pathway(maze_size, path_genes, pathway_map, horizontal_wall_map, vertical_wall_map)

        regions = self.divide_maze(maze_size, pathway_map)

        self.surround_regions(regions, horizontal_wall_map, vertical_wall_map)

        subregion_num = self.map_walls_of_regions(wall_genes, regions, maze_size, pathway_map, horizontal_wall_map, vertical_wall_map)
        genome.subregion_num = subregion_num

        self.surround_maze(horizontal_wall_map, vertical_wall_map)

        if save is not None:
            self.plot(save, maze_size, pathway_map, horizontal_wall_map, vertical_wall_map)

        if return_env:
            walls = self.extract_walls(maze_size, horizontal_wall_map, vertical_wall_map)

            start_point = (self.maze_scaler//2, self.maze_scaler//2)
            exit_point = (maze_size[0]*self.maze_scaler - self.maze_scaler//2,
                          maze_size[1]*self.maze_scaler - self.maze_scaler//2)

            timesteps = min(self.max_timesteps, int(path_length*self.maze_scaler*0.5))

            env = MazeEnvironment.make_environment(
                start_point, walls, exit_point,
                maze_kwargs=self.maze_kwargs, agent_kwargs=self.agent_kwargs)

            return env, timesteps

        else:
            return

    # track path reversely
    def track_pathway(self, maze_size, path_genes, path_map, h_wall_map, v_wall_map):
        path_length = 0
        end_p = (maze_size[0]-1, maze_size[1]-1)
        for gene in path_genes[::-1]:
            start_p = gene.pathpoint
            horizontal = gene.horizontal

            path_length += abs(end_p[0]-start_p[0])+abs(end_p[1]-start_p[1])
            self.mark_path(start_p, end_p, horizontal, path_map, h_wall_map, v_wall_map)

            end_p = start_p

        if (path_genes[-1].horizontal and path_genes[-1].pathpoint[1]!=maze_size[1]-1) or \
            (not path_genes[-1].horizontal and path_genes[-1].pathpoint[0]==maze_size[0]-1):
            v_wall_map[-1, -2] = True
            path_map[-1, -1] = 1
        else:
            h_wall_map[-2, -1] = True
            path_map[-1, -1] = 4
        return path_length

    def mark_path(self, start, end, horizontal, path_map, h_wall_map, v_wall_map):
        if horizontal:
            # afeter corner, vertical path
            if start[1]<end[1]:
                # mark path direction
                path_map[start[1]:end[1], end[0]] = 1 #south
                # map walls on both sides of path
                v_wall_map[start[1]:end[1], end[0]:end[0]+2] = True
                # map wall on tail of path
                h_wall_map[start[1], end[0]] = True
                # remove wall from head of path
                h_wall_map[end[1], end[0]] = False
            else:
                path_map[end[1]+1:start[1]+1, end[0]] = 3 #north
                v_wall_map[end[1]+1:start[1]+1, end[0]:end[0]+2] = True
                h_wall_map[start[1]+1, end[0]] = True
                h_wall_map[end[1]+1, end[0]] = False
            # before corner, horizontal path
            if start[0]<end[0]:
                path_map[start[1], start[0]:end[0]] = 4 #east
                h_wall_map[start[1]:start[1]+2, start[0]:end[0]] = True
                v_wall_map[start[1], start[0]] = True
                v_wall_map[start[1], end[0]] = False
            else:
                path_map[start[1], end[0]+1:start[0]+1] = 2 #west
                h_wall_map[start[1]:start[1]+2, end[0]+1:start[0]+1] = True
                v_wall_map[start[1], start[0]+1] = True
                v_wall_map[start[1], end[0]+1] = False
        else:
            # afeter corner, horizontal path
            if start[0]<end[0]:
                path_map[end[1], start[0]:end[0]] = 4
                h_wall_map[end[1]:end[1]+2, start[0]:end[0]] = True
                v_wall_map[end[1], start[0]] = True
                v_wall_map[end[1], end[0]] = False
            else:
                path_map[end[1], end[0]+1:start[0]+1] = 2
                h_wall_map[end[1]:end[1]+2, end[0]+1:start[0]+1] = True
                v_wall_map[end[1], start[0]+1] = True
                v_wall_map[end[1], end[0]+1] = False
            # before corner, vertical path
            if start[1]<end[1]:
                path_map[start[1]:end[1], start[0]] = 1
                v_wall_map[start[1]:end[1], start[0]:start[0]+2] = True
                h_wall_map[start[1], start[0]] = True
                h_wall_map[end[1], start[0]] = False
            else:
                path_map[end[1]+1:start[1]+1, start[0]] = 3
                v_wall_map[end[1]+1:start[1]+1, start[0]:start[0]+2] = True
                h_wall_map[start[1]+1, start[0]] = True
                h_wall_map[end[1]+1, start[0]] = False


    def divide_maze(self, maze_size, path_map):
        region_id = 1
        region_map = np.zeros((maze_size[1], maze_size[0]), dtype=int)
        region_map[path_map>0] = -1
        regions = {}
        for y,x in zip(*np.where(region_map==0)):
            if region_map[y,x]!=0:
                continue

            cut_out = region_map[y:y+self.region_max_size[1], x:x+self.region_max_size[0]]

            if np.all(cut_out==0):
                r_height, r_width = cut_out.shape

            else:
                # width-first square
                x_width = cut_out.shape[1] if np.all(cut_out[0,:]==0) else np.where(cut_out[0,:]!=0)[0][0]
                x_height = cut_out.shape[0] if np.all(cut_out[:,:x_width]==0) else np.where(np.any(cut_out[:,:x_width]!=0,axis=1))[0][0]
                # height-first square
                y_height = cut_out.shape[0] if np.all(cut_out[:,0]==0) else np.where(cut_out[:,0]!=0)[0][0]
                y_width = cut_out.shape[1] if np.all(cut_out[:y_height,:]==0) else np.where(np.any(cut_out[:y_height,:]!=0,axis=0))[0][0]

                # chose the one with the lerger square area
                if x_width*x_height > y_width*y_height:
                    r_width = x_width
                    r_height = x_height
                else:
                    r_width = y_width
                    r_height = y_height

            # map the region id
            region_map[y:y+r_height, x:x+r_width] = region_id
            regions[region_id] = {
                'id': region_id,
                'point': (x,y),
                'size': (r_width, r_height),
                'depth': 1,
                # 'root_id': region_id,
            }
            region_id += 1

        return regions


    def surround_regions(self, regions, h_wall_map, v_wall_map):
        for region in regions.values():
            start_p = region['point']
            end_p = (start_p[0]+region['size'][0], start_p[1]+region['size'][1])

            h_wall_map[start_p[1], start_p[0]:end_p[0]] = True
            h_wall_map[end_p[1]  , start_p[0]:end_p[0]] = True
            v_wall_map[start_p[1]:end_p[1], start_p[0]] = True
            v_wall_map[start_p[1]:end_p[1], end_p[0]  ] = True


    def map_walls_of_regions(self, wall_genes, regions, maze_size, path_map, h_wall_map, v_wall_map):

        subregion_queue = list(regions.values())
        # region_idx = {region_id: 0 for region_id in regions.keys()}
        region_idx = 0
        region_id = max(regions.keys())

        while subregion_queue:
            subregion = subregion_queue.pop(0)

            r_id = subregion['id']
            r_width, r_height = subregion['size']
            r_start = subregion['point']
            r_end = (r_start[0]+r_width, r_start[1]+r_height)
            r_depth = subregion['depth']
            # r_root = subregion['root_id']

            if r_width<self.region_min_size[0] or r_height<self.region_min_size[1]:
                if r_depth==1:
                    v_point = r_start
                    h_point = r_start
                    self.make_entrance(h_point, v_point, r_start, r_end, maze_size, path_map, h_wall_map, v_wall_map)
                continue

            # wall_idx = region_idx[r_root]%len(wall_genes)
            # region_idx[r_root] += 1
            wall_idx = region_idx%len(wall_genes)
            region_idx += 1

            wall_loc_rel = wall_genes[wall_idx].wall_location
            passage_loc_rel = wall_genes[wall_idx].passage_location
            horizontal = wall_genes[wall_idx].horizontal

            if horizontal:
                wall_y = int((r_height-1)*wall_loc_rel)+1
                passage_x = int(r_width*passage_loc_rel)

                if passage_x>0:
                    h_wall_map[r_start[1]+wall_y, r_start[0]:r_start[0]+passage_x] = True
                if passage_x+1<r_width:
                    h_wall_map[r_start[1]+wall_y, r_start[0]+passage_x+1:r_start[0]+r_width] = True

                if wall_y>=2:
                    region_id += 1
                    subregion_queue.append({
                        'id': region_id,
                        'point': r_start,
                        'size': (r_width, wall_y),
                        'depth': r_depth+1,
                        # 'root_id': r_root,
                    })
                if r_height-wall_y>=2:
                    region_id += 1
                    subregion_queue.append({
                        'id': region_id,
                        'point': (r_start[0], r_start[1]+wall_y),
                        'size': (r_width, r_height-wall_y),
                        'depth': r_depth+1,
                        # 'root_id': r_root,
                    })

                if r_depth==1:
                    v_point = (r_start[0]+passage_x, r_start[1])
                    h_point = (r_start[0], r_start[1]+wall_y)
                    self.make_entrance(h_point, v_point, r_start, r_end, maze_size, path_map, h_wall_map, v_wall_map)

            else:
                wall_x = int((r_width-1)*wall_loc_rel)+1
                passage_y = int(r_height*passage_loc_rel)

                if passage_y>0:
                    v_wall_map[r_start[1]:r_start[1]+passage_y, r_start[0]+wall_x] = True
                if passage_y+1<r_height:
                    v_wall_map[r_start[1]+passage_y+1:r_start[1]+r_height, r_start[0]+wall_x] = True

                if wall_x>=2:
                    region_id += 1
                    subregion_queue.append({
                        'id': region_id,
                        'point': r_start,
                        'size': (wall_x, r_height),
                        'depth': r_depth+1,
                        # 'root_id': r_root,
                    })
                if r_width-wall_x>=2:
                    region_id += 1
                    subregion_queue.append({
                        'id': region_id,
                        'point': (r_start[0]+wall_x, r_start[1]),
                        'size': (r_width-wall_x, r_height),
                        'depth': r_depth+1,
                        # 'root_id': r_root,
                    })

                if r_depth==1:
                    v_point = (r_start[0]+wall_x, r_start[1])
                    h_point = (r_start[0], r_start[1]+passage_y)
                    self.make_entrance(h_point, v_point, r_start, r_end, maze_size, path_map, h_wall_map, v_wall_map)

        return region_idx

    def make_entrance(self, h_point, v_point, start_p, end_p, maze_size, path_map, h_wall_map, v_wall_map):
        step = 1
        # search pathway
        while step<maze_size[0] or step<maze_size[1]:
            # toward east
            if h_point[0]+step<maze_size[0] and path_map[h_point[1], h_point[0]+step]>0:
                v_wall_map[h_point[1], end_p[0]] = False
                break
            # toward west
            if h_point[0]-step>=0 and path_map[h_point[1], h_point[0]-step]>0:
                v_wall_map[h_point[1], start_p[0]] = False
                break
            # toward south
            if v_point[1]+step<maze_size[1] and path_map[v_point[1]+step, v_point[0]]>0:
                h_wall_map[end_p[1], v_point[0]] = False
                break
            # toward north
            if v_point[1]-step>=0 and path_map[v_point[1]-step, v_point[0]]>0:
                h_wall_map[start_p[1], v_point[0]] = False
                break
            step += 1

    def surround_maze(self, h_wall_map, v_wall_map):
        h_wall_map[0,:] = True
        h_wall_map[-1,:] = True
        v_wall_map[:,0] = True
        v_wall_map[:,-1] = True


    def extract_walls(self, maze_size, h_wall_map, v_wall_map):
        walls = []
        for h_i in range(maze_size[1]+1):
            no_walls = list(np.where(h_wall_map[h_i,:]==False)[0])
            no_walls.append(maze_size[0])
            prev_i = 0
            for now_i in no_walls:
                if prev_i<now_i:
                    walls.append(
                        (prev_i*self.maze_scaler, h_i*self.maze_scaler, #start point
                         now_i *self.maze_scaler, h_i*self.maze_scaler) #end point
                    )
                prev_i = now_i+1

        for w_i in range(maze_size[0]+1):
            no_walls = list(np.where(v_wall_map[:,w_i]==False)[0])
            no_walls.append(maze_size[1])
            prev_i = 0
            for now_i in no_walls:
                if prev_i<now_i:
                    walls.append(
                        (w_i*self.maze_scaler, prev_i*self.maze_scaler, #start point
                         w_i*self.maze_scaler, now_i *self.maze_scaler) #end point
                    )
                prev_i = now_i+1

        return walls

    def plot(self, save_path, maze_size, path_map, h_wall_map, v_wall_map):
        fig, ax = plt.subplots(figsize=(maze_size[0]/2, maze_size[1]/2))

        arrow_args = {
            'width':0.03,
            'head_width':0.2,
            'head_length':0.15,
            'fc':'k',
            'length_includes_head':True
        }
        for j,i in zip(*np.where(path_map>0)):
            if (i,j)==(0,0) or (i,j)==(maze_size[0]-1,maze_size[1]-1):
                continue
            if path_map[j,i]==1:
                ax.arrow(x=i+0.5,y=j+0.25,dx=0,dy=0.5,**arrow_args)
            elif path_map[j,i]==2:
                ax.arrow(x=i+0.75,y=j+0.5,dx=-0.5,dy=0,**arrow_args)
            elif path_map[j,i]==3:
                ax.arrow(x=i+0.5,y=j+0.75,dx=0,dy=-0.5,**arrow_args)
            elif path_map[j,i]==4:
                ax.arrow(x=i+0.25,y=j+0.5,dx=0.5,dy=0,**arrow_args)

        ax.scatter(0.5, 0.5, color=[0.0,0.6,0.3], s=96, marker='s')
        ax.scatter(maze_size[0]-0.5, maze_size[1]-0.5, color=[0.9,0.2,0.0], s=128, marker='*')

        for h_i in range(maze_size[1]+1):
            no_walls = list(np.where(h_wall_map[h_i,:]==False)[0])
            no_walls.append(maze_size[0])
            prev_i = 0
            for now_i in no_walls:
                if prev_i<now_i:
                    ax.plot([prev_i, now_i], [h_i, h_i], c='k', linewidth=3)
                prev_i = now_i+1

        for w_i in range(maze_size[0]+1):
            no_walls = list(np.where(v_wall_map[:,w_i]==False)[0])
            no_walls.append(maze_size[1])
            prev_i = 0
            for now_i in no_walls:
                if prev_i<now_i:
                    ax.plot([w_i, w_i], [prev_i, now_i], c='k', linewidth=3)
                prev_i = now_i+1

        ax.axis('off')
        plt.savefig(save_path, bbox_inches='tight')
        plt.cla()
