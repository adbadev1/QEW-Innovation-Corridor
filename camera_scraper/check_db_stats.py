from database import CameraDatabase

db = CameraDatabase('camera_data.db')

print('=' * 60)
print('DATABASE STATISTICS')
print('=' * 60)

db.cursor.execute('SELECT COUNT(*) FROM cameras')
print(f'Total Cameras: {db.cursor.fetchone()[0]}')

db.cursor.execute('SELECT COUNT(*) FROM images')
print(f'Total Images: {db.cursor.fetchone()[0]}')

db.cursor.execute('SELECT COUNT(*) FROM collections')
print(f'Total Collections: {db.cursor.fetchone()[0]}')

print('\n' + '=' * 60)
print('LATEST COLLECTION')
print('=' * 60)

db.cursor.execute('SELECT * FROM collections ORDER BY start_time DESC LIMIT 1')
coll = dict(db.cursor.fetchone())
print(f'Collection ID: {coll["collection_id"]}')
print(f'Status: {coll["status"]}')
print(f'Total Images: {coll["total_images"]}')
print(f'Directory: {coll["output_directory"]}')

print('\n' + '=' * 60)
print('SAMPLE IMAGES FROM LATEST COLLECTION')
print('=' * 60)

db.cursor.execute('SELECT * FROM images WHERE collection_id = ? LIMIT 5', (coll["collection_id"],))
for img in db.cursor.fetchall():
    img_dict = dict(img)
    print(f'\n{img_dict["filename"]}')
    print(f'  Camera: {img_dict["camera_id"]} | View: {img_dict["view_id"]}')
    print(f'  Location: {img_dict["location"]}')
    print(f'  GPS: ({img_dict["latitude"]}, {img_dict["longitude"]})')

db.close()

