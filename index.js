import { Sequelize, DataTypes } from 'sequelize';
import fs from 'fs'

const decoder = new TextDecoder();
const encoder = new TextEncoder();

const sequelize = new Sequelize('', '', '', {
    host: '',
    dialect: 'mysql',
    logging:false,
    define: {
        freezeTableName: true
    }
});

const VicidialList = sequelize.define(
    'numeros',
    {
        numero: DataTypes.STRING,
        operador: DataTypes.STRING,
        fecha_consulta: DataTypes.STRING
    },
    {
        createdAt: false,
        updatedAt: false
    }
)

VicidialList.removeAttribute('createdAt');
VicidialList.removeAttribute('updatedAt');

try {
    await sequelize.authenticate();
    console.log('Connection has been established successfully.');
} catch (error) {
    console.error('Unable to connect to the database:', error);
}

fs.readFile('./datos.csv', 'utf-8', async(err, file) => {
    const lines = file.split('\n')
    let project
    let contador = 0
    for (let line of lines)
        if (!line.includes('NUMERO')) {
            project = await VicidialList.findOne({ where: { numero: line.split(',')[0]} });
            if (!project){
                let numero, operador, fecha
                numero = line.split(',')[0]
                if (line.split(',').length == 3) {
                    operador = line.split(',')[1] 
                    fecha = line.split(',')[2]
                }
                if (line.split(',').length == 4){
                    operador = line.split(',')[1] + line.split(',')[2]
                    fecha = line.split(',')[3]
                }
                await VicidialList.create({ numero: numero, operador:operador, fecha_consulta: fecha });
            }
            else {
                console.log(project.dataValues);
                
            }
        }        
        //console.log(line.split(",").length)
});