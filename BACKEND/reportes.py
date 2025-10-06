# reportes.py
# Módulo de gestión de reportes con MongoDB

from flask import Blueprint, request, jsonify, send_file
from functools import wraps
import jwt
from config import JWT_SECRET, JWT_ALGORITHM
from database import tickets_collection, peliculas_collection, salas_collection
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO

reportes_bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Token mal formateado'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token faltante'}), 401
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        user_data = request.current_user
        if user_data.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador'
            }), 403
        return f(*args, **kwargs)
    
    return decorated


# ✅ Función auxiliar para convertir precio a float de forma segura
def convertir_precio(precio):
    """Convierte el precio a float, manejando strings y números"""
    try:
        if isinstance(precio, str):
            # Remover símbolos de moneda y espacios
            precio = precio.replace('$', '').replace(',', '').strip()
        return float(precio)
    except (ValueError, TypeError):
        return 0.0


# Agregar este endpoint al archivo reportes.py después de los imports y antes de los otros endpoints

@reportes_bp.route('/estadisticas-rapidas', methods=['GET'])
@jwt_required
def obtener_estadisticas_rapidas():
    """Obtener estadísticas rápidas para el dashboard"""
    try:
        from datetime import datetime, timedelta
        
        # Fecha de hoy
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        # 1. Total de películas activas
        total_peliculas = peliculas_collection.count_documents({"estado": "activo"})
        
        # 2. Tickets vendidos hoy
        tickets_hoy = tickets_collection.count_documents({
            "fecha_funcion": hoy,
            "estado": {"$in": ["pagado", "reservado"]}
        })
        
        # 3. Ingresos de hoy
        tickets_hoy_data = list(tickets_collection.find({
            "fecha_funcion": hoy,
            "estado": {"$in": ["pagado", "reservado"]}
        }))
        ingresos_hoy = sum(convertir_precio(t.get('precio', 0)) for t in tickets_hoy_data)
        
        # 4. Total de salas
        total_salas = salas_collection.count_documents({})
        
        # 5. Total de usuarios (si tienes acceso a la colección)
        try:
            from database import usuarios_collection
            total_usuarios = usuarios_collection.count_documents({})
        except:
            total_usuarios = 0
        
        # 6. Tickets de la semana pasada para comparación
        hace_7_dias = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        tickets_semana_pasada = tickets_collection.count_documents({
            "fecha_funcion": {"$gte": hace_7_dias, "$lt": hoy},
            "estado": {"$in": ["pagado", "reservado"]}
        })
        
        # Calcular porcentaje de cambio
        if tickets_semana_pasada > 0:
            cambio_tickets = ((tickets_hoy - (tickets_semana_pasada / 7)) / (tickets_semana_pasada / 7)) * 100
        else:
            cambio_tickets = 100 if tickets_hoy > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_peliculas': total_peliculas,
                'tickets_vendidos_hoy': tickets_hoy,
                'ingresos_hoy': round(ingresos_hoy, 2),
                'total_salas': total_salas,
                'total_usuarios': total_usuarios,
                'cambio_tickets': round(cambio_tickets, 2),
                'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200
        
    except Exception as e:
        print(f"Error en estadisticas_rapidas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500

@reportes_bp.route('/ventas', methods=['GET'])
@admin_required
def generar_reporte_ventas():
    """Generar reporte de ventas en JSON"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Construir filtro
        filtro = {"estado": {"$in": ["pagado", "reservado"]}}
        
        if fecha_inicio:
            if 'fecha_funcion' not in filtro:
                filtro['fecha_funcion'] = {}
            filtro['fecha_funcion']['$gte'] = fecha_inicio
        
        if fecha_fin:
            if 'fecha_funcion' not in filtro:
                filtro['fecha_funcion'] = {}
            filtro['fecha_funcion']['$lte'] = fecha_fin
        
        # Obtener tickets
        tickets = list(tickets_collection.find(filtro))
        for t in tickets:
            t['_id'] = str(t['_id'])
        
        # ✅ Calcular estadísticas con conversión de tipos
        total_tickets = len(tickets)
        ingresos_totales = sum(convertir_precio(t.get('precio', 0)) for t in tickets)
        
        # Ventas por película
        ventas_pelicula = {}
        for t in tickets:
            pelicula = t.get('pelicula_nombre', 'Desconocida')
            if pelicula not in ventas_pelicula:
                ventas_pelicula[pelicula] = {'cantidad': 0, 'ingresos': 0.0}
            ventas_pelicula[pelicula]['cantidad'] += 1
            ventas_pelicula[pelicula]['ingresos'] += convertir_precio(t.get('precio', 0))
        
        # Ventas por sala
        ventas_sala = {}
        for t in tickets:
            sala = t.get('sala_nombre', 'Desconocida')
            if sala not in ventas_sala:
                ventas_sala[sala] = {'cantidad': 0, 'ingresos': 0.0}
            ventas_sala[sala]['cantidad'] += 1
            ventas_sala[sala]['ingresos'] += convertir_precio(t.get('precio', 0))
        
        # ✅ Redondear ingresos en las ventas por película y sala
        for pelicula in ventas_pelicula:
            ventas_pelicula[pelicula]['ingresos'] = round(ventas_pelicula[pelicula]['ingresos'], 2)
        
        for sala in ventas_sala:
            ventas_sala[sala]['ingresos'] = round(ventas_sala[sala]['ingresos'], 2)
        
        return jsonify({
            'success': True,
            'message': 'Reporte generado exitosamente',
            'data': {
                'resumen': {
                    'total_tickets': total_tickets,
                    'ingresos_totales': round(ingresos_totales, 2),
                    'fecha_inicio': fecha_inicio or 'Todas',
                    'fecha_fin': fecha_fin or 'Todas'
                },
                'ventas_por_pelicula': ventas_pelicula,
                'ventas_por_sala': ventas_sala,
                'tickets': tickets
            }
        }), 200
        
    except Exception as e:
        print(f"Error en generar_reporte_ventas: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al generar reporte: {str(e)}'
        }), 500


@reportes_bp.route('/ventas/pdf', methods=['GET'])
@admin_required
def generar_reporte_ventas_pdf():
    """Generar reporte de ventas en PDF"""
    try:
        fecha_inicio = request.args.get('fecha_inicio', 'Todas')
        fecha_fin = request.args.get('fecha_fin', 'Todas')
        
        # Construir filtro
        filtro = {"estado": {"$in": ["pagado", "reservado"]}}
        
        if fecha_inicio != 'Todas':
            if 'fecha_funcion' not in filtro:
                filtro['fecha_funcion'] = {}
            filtro['fecha_funcion']['$gte'] = fecha_inicio
        
        if fecha_fin != 'Todas':
            if 'fecha_funcion' not in filtro:
                filtro['fecha_funcion'] = {}
            filtro['fecha_funcion']['$lte'] = fecha_fin
        
        # Obtener tickets
        tickets = list(tickets_collection.find(filtro))
        
        # ✅ Calcular estadísticas con conversión de tipos
        total_tickets = len(tickets)
        ingresos_totales = sum(convertir_precio(t.get('precio', 0)) for t in tickets)
        
        # Ventas por película
        ventas_pelicula = {}
        for t in tickets:
            pelicula = t.get('pelicula_nombre', 'Desconocida')
            if pelicula not in ventas_pelicula:
                ventas_pelicula[pelicula] = {'cantidad': 0, 'ingresos': 0.0}
            ventas_pelicula[pelicula]['cantidad'] += 1
            ventas_pelicula[pelicula]['ingresos'] += convertir_precio(t.get('precio', 0))
        
        # Crear PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a56db'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Título
        story.append(Paragraph("CineMax - Reporte de Ventas", titulo_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Información del reporte
        info_data = [
            ['Fecha de generación:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            ['Período:', f'{fecha_inicio} - {fecha_fin}'],
            ['Usuario:', request.current_user.get('email', 'N/A')]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Resumen ejecutivo
        story.append(Paragraph("Resumen Ejecutivo", subtitulo_style))
        
        # ✅ Usar conversión segura para precio promedio
        precio_promedio = (ingresos_totales / total_tickets) if total_tickets > 0 else 0
        
        resumen_data = [
            ['Métrica', 'Valor'],
            ['Total de Tickets Vendidos', str(total_tickets)],
            ['Ingresos Totales', f'${ingresos_totales:,.2f}'],
            ['Precio Promedio', f'${precio_promedio:,.2f}']
        ]
        
        resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))
        
        story.append(resumen_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Ventas por película
        story.append(Paragraph("Ventas por Película", subtitulo_style))
        
        pelicula_data = [['Película', 'Tickets', 'Ingresos']]
        for pelicula, datos in sorted(ventas_pelicula.items(), key=lambda x: x[1]['ingresos'], reverse=True):
            pelicula_data.append([
                pelicula,
                str(datos['cantidad']),
                f"${datos['ingresos']:,.2f}"
            ])
        
        # ✅ Manejar caso sin datos
        if len(pelicula_data) == 1:
            pelicula_data.append(['Sin datos', '0', '$0.00'])
        
        pelicula_table = Table(pelicula_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        pelicula_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))
        
        story.append(pelicula_table)
        
        # Construir PDF
        doc.build(story)
        
        # Preparar respuesta
        buffer.seek(0)
        filename = f"reporte_ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error al generar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al generar PDF: {str(e)}'
        }), 500


@reportes_bp.route('/ocupacion', methods=['GET'])
@admin_required
def generar_reporte_ocupacion():
    """Generar reporte de ocupación de salas"""
    try:
        fecha = request.args.get('fecha')
        
        if not fecha:
            return jsonify({
                'success': False,
                'message': 'La fecha es requerida'
            }), 400
        
        # Obtener todas las salas
        salas = list(salas_collection.find())
        
        reporte = []
        for sala in salas:
            # Contar tickets vendidos para esa sala en esa fecha
            tickets_vendidos = tickets_collection.count_documents({
                "sala_id": sala['id'],
                "fecha_funcion": fecha,
                "estado": {"$in": ["pagado", "reservado"]}
            })
            
            capacidad = sala['capacidad']
            ocupacion = (tickets_vendidos / capacidad * 100) if capacidad > 0 else 0
            
            reporte.append({
                'sala': sala['nombre'],
                'capacidad': capacidad,
                'tickets_vendidos': tickets_vendidos,
                'asientos_disponibles': capacidad - tickets_vendidos,
                'porcentaje_ocupacion': round(ocupacion, 2)
            })
        
        return jsonify({
            'success': True,
            'message': 'Reporte de ocupación generado',
            'data': {
                'fecha': fecha,
                'salas': reporte
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al generar reporte: {str(e)}'
        }), 500